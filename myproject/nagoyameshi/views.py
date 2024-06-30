from django.shortcuts import render,redirect
from django.views.generic import ListView, DetailView
from .models import Restaurant,  CustomUser, Category, Review, Reservation #レストランモデル、新規会員登録モデルのインポート 
from django.contrib.auth import login, authenticate #ログイン、認証のモデル
from django.contrib.auth.views import LogoutView  # LogoutViewをインポート
from django.contrib.auth.hashers import make_password  # パスワードハッシュ化をインポート
from django.http import HttpResponse  # HttpResponseをインポート（HTMLをレンダリングしない）
from django.core.mail import send_mail #以下会員登録時メール認証用インポート
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_protect, csrf_exempt  # CSRF保護のためのデコレータをインポート
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import datetime


# トップページ用（レストランリスト）のビュー
class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'restaurant_list.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')
        category = self.request.GET.get('category')
        if name:
            queryset = queryset.filter(name__icontains=name)
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # すべてのカテゴリをテンプレートに渡す
        return context

#レストラン詳細ビュー
class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = 'restaurant_detail.html'
    context_object_name = 'restaurant'

    def get_context_data(self, **kwargs):#レビューの引き渡し
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(restaurant=self.object)
        return context

# 新規会員登録用のビュー
@csrf_protect
def signup(request):#requestオブジェクトに含まれる情報の受け取り
    if request.method == 'POST':#会員登録のリクエストがされたら
        full_name = request.POST['full_name']
        furigana = request.POST['furigana']
        postal_code = request.POST['postal_code']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        birthdate = request.POST['birthdate']
        occupation = request.POST['occupation']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        # バリデーション
        if password1 != password2:
            return HttpResponse("Passwords do not match.")
        if CustomUser.objects.filter(email=email).exists():
            return HttpResponse("Email already exists.")

        # ユーザー作成
        user = CustomUser(
            full_name=full_name,
            furigana=furigana,
            postal_code=postal_code,
            address=address,
            phone_number=phone_number,
            birthdate=birthdate,
            occupation=occupation,
            email=email,
            password=make_password(password1),
            is_end_user=True,
            is_active = False #認証前なのでアカウントを無効化
        )
        user.save()#ユーザー情報をDBに保存

        #アカウント有効化メールの送信
        current_site = get_current_site(request)
        mail_subject = 'Activate your account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        send_mail(mail_subject, message, 'noreply@mydomain.com', [email])

        return HttpResponse('Please confirm your email address to complete the registration.')

    return render(request, 'signup.html')

#アカウント有効化用のビュー
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!') 

#ログインビュー
@csrf_protect
def login_view(request):
    if request.method =='POST':
       email = request.POST['email']
       password = request.POST['password']
       user = authenticate(request, username=email, password=password)
       
       if user is not None:
        login(request, user)
        return redirect('restaurant_list')
    
       else:
        return HttpResponse("Invalid email or password")
    return render(request, 'login.html')
    
# 予約作成ビュー
@login_required
@csrf_protect
def make_reservation(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    if request.method == 'POST':
        reservation_date = request.POST['reservation_date']
        reservation_time = request.POST['reservation_time']
        number_of_people = request.POST['number_of_people']
        
        # 予約重複チェック
        if Reservation.objects.filter(restaurant=restaurant, reservation_date=reservation_date, reservation_time=reservation_time).exists():
            return HttpResponse("The selected date and time is already booked.")

        # 予約作成
        reservation = Reservation.objects.create(
            user=request.user,
            restaurant=restaurant,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            number_of_people=number_of_people
        )
        
        # 予約完了メールの送信
        current_site = get_current_site(request)
        mail_subject = 'Reservation Confirmation'
        message = render_to_string('reservation_email.html', {
            'user': request.user,
            'restaurant': restaurant,
            'reservation': reservation,
            'domain': current_site.domain,
        })
        send_mail(mail_subject, message, 'noreply@mydomain.com', [request.user.email])

        return redirect('reservation_list')

    return render(request, 'make_reservation.html', {'restaurant': restaurant})

# 予約リストビュー
@login_required
def reservation_list(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'reservation_list.html', {'reservations': reservations})

# 予約キャンセルビュー
@login_required
def cancel_reservation(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)
    if reservation.user == request.user:
        reservation.delete()
    return redirect('reservation_list')