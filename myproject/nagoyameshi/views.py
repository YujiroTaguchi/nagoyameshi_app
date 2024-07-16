from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from .models import Restaurant, CustomUser, Category, Review, Reservation, Favorite, Subscription
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import datetime
import stripe
from django.conf import settings
from django.urls import reverse
from django.db.models import Avg 
from .decorators import subscription_required  # カスタムデコレータをインポート

# StripeのAPIキーを設定
stripe.api_key = settings.STRIPE_SECRET_KEY

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
        context['categories'] = Category.objects.all()
        for restaurant in context['restaurants']:
            avg_rating = Review.objects.filter(restaurant=restaurant).aggregate(Avg('rating'))['rating__avg']
            restaurant.avg_rating = round(avg_rating, 2) if avg_rating else None
        return context

# レストラン詳細ビュー
class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = 'restaurant_detail.html'
    context_object_name = 'restaurant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(restaurant=self.object)
        avg_rating = Review.objects.filter(restaurant=self.object).aggregate(Avg('rating'))['rating__avg']
        context['avg_rating'] = round(avg_rating, 2) if avg_rating else None
        return context
    
# 新規会員登録用のビュー
@csrf_protect
def signup(request):
    if request.method == 'POST':
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
        
        if password1 != password2:
            return HttpResponse("Passwords do not match.")
        if CustomUser.objects.filter(email=email).exists():
            return HttpResponse("Email already exists.")

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
            is_active=False #ユーザーを非有効化
        )
        user.save()

        current_site = get_current_site(request)
        mail_subject = 'Activate your account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        activation_url = reverse('activate', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })
        send_mail(mail_subject, message, 'noreply@mydomain.com', [email])

        return HttpResponse('Please confirm your email address to complete the registration.')

    return render(request, 'signup.html')

# アカウント有効化用のビュー
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
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

# ログインビュー
@csrf_protect
def login_view(request):
    if request.method == 'POST':
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
@subscription_required
@csrf_protect
def make_reservation(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        reservation_date = request.POST['reservation_date']
        reservation_time = request.POST['reservation_time']
        number_of_people = request.POST['number_of_people']
        
        if Reservation.objects.filter(restaurant=restaurant, reservation_date=reservation_date, reservation_time=reservation_time).exists():
            return HttpResponse("The selected date and time is already booked.")

        reservation = Reservation.objects.create(
            user=request.user,
            restaurant=restaurant,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            number_of_people=number_of_people
        )

        current_site = get_current_site(request)
        mail_subject = 'Reservation Confirmation'
        message = render_to_string('reservation_email.html', {
            'user': request.user,
            'restaurant': restaurant,
            'reservation': reservation,
            'domain': current_site.domain,
        })
        send_mail(mail_subject, message, 'noreply@mydomain.com', [request.user.email])

        return redirect('reservation_success', reservation_id=reservation.id)

    return render(request, 'make_reservation.html', {'restaurant': restaurant})

@login_required
@subscription_required
def reservation_success(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    return render(request, 'reservation_success.html', {'reservation': reservation})


# 予約リストビュー
@login_required
@subscription_required
def reservation_list(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'reservation_list.html', {'reservations': reservations})

# 予約キャンセルビュー
@login_required
@subscription_required
def cancel_reservation(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)
    if reservation.user == request.user:
        reservation.delete()
    return redirect('reservation_list')

# お気に入り追加ビュー
@login_required
@subscription_required
def add_to_favorites(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)
    return redirect('restaurant_detail', pk=restaurant_id)

# お気に入り解除ビュー
@login_required
@subscription_required
def remove_from_favorites(request, favorite_id):
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    favorite.delete()
    return redirect('favorite_list')

# お気に入り一覧ビュー
@login_required
@subscription_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('restaurant')
    return render(request, 'favorite_list.html', {'favorites': favorites})

# マイページビュー
@login_required
def mypage(request):
    user = request.user
    if user.is_subscription_user:
        reservations = Reservation.objects.filter(user=user)
        favorites = Favorite.objects.filter(user=user)
        return render(request, 'mypage_subscription.html', {'user': user, 'reservations': reservations, 'favorites': favorites})
    else:
        return render(request, 'mypage_free.html', {'user': user})
# ユーザー情報編集ビュー
@login_required
@csrf_protect
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.full_name = request.POST['full_name']
        user.furigana = request.POST['furigana']
        user.postal_code = request.POST['postal_code']
        user.address = request.POST['address']
        user.phone_number = request.POST['phone_number']
        user.birthdate = request.POST['birthdate']
        user.occupation = request.POST['occupation']
        user.save()
        return redirect('mypage')
    return render(request, 'edit_profile.html', {'user': user})


# StripeのCheckoutセッション作成ビュー
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': 'price_1PYjlTRw1PAgyvNA5zi02qT7',  # 実際の価格IDに置き換えます
                        'quantity': 1,
                    },
                ],  
                mode='subscription',
                success_url=YOUR_DOMAIN + '/success/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=YOUR_DOMAIN + '/cancel/',
            )
            return redirect(checkout_session.url)
        except Exception as e:
            print('Error creating checkout session:', e)
            return JsonResponse({'error': str(e)}, status=500) 
            
# Stripe支払い成功時のビュー
class SuccessView(View):
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')

        if session_id is None:
            return HttpResponse("Session ID not found.", status=400)

        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            subscription_id = checkout_session['subscription']

            user = request.user
            user.is_subscription_user = True
            user.stripe_customer_id = checkout_session['customer']
            user.stripe_subscription_id = subscription_id
            user.save()

            return render(request, "success.html")
        except Exception as e:
            print(f"Error retrieving checkout session: {e}")
            return HttpResponse("Error retrieving checkout session.", status=500)
        
# Stripe支払いキャンセル時のビュー
class CancelView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "cancel.html")

# ログアウトビュー
def logout_view(request):
    logout(request)
    return redirect('login')

# 解約機能の追加
def cancel_subscription(request):
    user = request.user
    try:
        # サブスクリプションIDを取得する（ユーザーモデルに保存されている場合）
        subscription_id = user.stripe_subscription_id
        if subscription_id:
            # サブスクリプションをキャンセル
            stripe.Subscription.cancel(subscription_id)
            
            # ユーザーモデルのサブスクリプションステータスを更新
            user.is_subscription_user = False
            user.stripe_subscription_id = None  # サブスクリプションIDをクリア
            user.save()
            
            return redirect('mypage')
        else:
            return HttpResponse("No subscription found.")
    except Exception as e:
        print(f"Error cancelling subscription: {e}")
        return HttpResponse("Error cancelling subscription. Please try again later.")
    
 # レビュー投稿ビュー
@login_required
@subscription_required
def add_review(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        rating = request.POST['rating']
        comment = request.POST['comment']
        Review.objects.create(user=request.user, restaurant=restaurant, rating=rating, comment=comment)
        return redirect('restaurant_detail', pk=restaurant.id)
    return render(request, 'add_review.html', {'restaurant': restaurant})

# レビュ編集ュー
@login_required
@subscription_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        review.rating = request.POST['rating']
        review.comment = request.POST['comment']
        review.save()
        return redirect('restaurant_detail', pk=review.restaurant.id)
    return render(request, 'edit_review.html', {'review': review})

# レビュー削除ビュー
@login_required
@subscription_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    restaurant_id = review.restaurant.id
    review.delete()
    return redirect('restaurant_detail', pk=restaurant_id)

# StripeのBilling Portalセッションを作成するビュー
@login_required
def create_billing_portal_session(request):
    try:
        session = stripe.billing_portal.Session.create(
            customer=request.user.stripe_customer_id,
            return_url="http://127.0.0.1:8000/mypage/",
        )
        return redirect(session.url)
    except Exception as e:
        print(f"Error creating billing portal session: {e}")
        return HttpResponse("Error creating billing portal session. Please try again later.", status=500)
    
#エラーページビューの追加
def subscription_required_view(request):
    return render(request, 'subscription_required.html')