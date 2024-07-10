from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager #Djangoのユーザー、管理者登録標準モデル

# カテゴリモデルの定義
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# レストラン登録のモデル作成
class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    description = models.TextField()
    postal_code = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    open_time = models.TimeField()
    close_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.TimeField(auto_now=True)
    img = models.ImageField(upload_to='restaurant_images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
         return self.name

  #管理者設定
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)    
  #ユーザー登録モデルの作成
class CustomUser(AbstractUser):#フィールドとメソッド（PW検証など）を継承
    username = None  # usernameフィールドを無効化（DBから削除）
    email = models.EmailField(unique=True)  # DB内のメールアドレスを一意に設定
    full_name = models.CharField(max_length=100)#以下フィールドの設定
    furigana = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    birthdate = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100)

    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)#ストライプAPI
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)#ストライプAPI

    is_end_user = models.BooleanField(default=False)#カスタムでエンドユーザーかどうかのフラグを追加
    is_admin_user = models.BooleanField(default=False)#管理者かどうかのフラグを追加
    is_subscription_user = models.BooleanField(default=False)  # 有料会員かどうかのフラグを追加

    USERNAME_FIELD = 'email'  # メールアドレスを認証に使用
    REQUIRED_FIELDS = ['full_name', 'furigana', 'postal_code', 'address', 'phone_number', 'birthdate', 'occupation']

    objects = CustomUserManager()  ### CustomUserManagerをオブジェクトとして設定
    
    def __str__(self):
            return self.email #メールアドレスを文字列として返す（管理画面用）  

class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user} for {self.restaurant}'
    
# 予約モデルの作成
class Reservation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_people = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.full_name} - {self.restaurant.name} - {self.reservation_date} {self.reservation_time}'
    
    # お気に入りモデルの定義
class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.full_name} likes {self.restaurant.name}'
    
# 有料会員登録モデルの定義
class Subscription(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)  # StripeのサブスクリプションID
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.email} - {"Active" if self.is_active else "Inactive"}'