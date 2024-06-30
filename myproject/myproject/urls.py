"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from nagoyameshi import views
from django.conf import settings
from django.conf.urls.static import static
from nagoyameshi.views import signup, login_view, activate, RestaurantDetailView, make_reservation, reservation_list, cancel_reservation   # 新規会員登録のsignup、login、メールアクティベイトビュー関数をインポート
from django.contrib.auth.views import LogoutView  # ログアウトビューの追加

urlpatterns = [
    path('admin/', admin.site.urls),
     path('restaurants/', views.RestaurantListView.as_view(), name='restaurant_list'),
       path('restaurants/<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant_detail'),  # 詳細ビューのURLパターン
     path('signup/', views.signup, name='signup'),#URL,ビュー関数、URL名
     path('login/', login_view, name='login'),#ログイン用URL
       path('logout/', LogoutView.as_view(next_page='restaurant_list'), name='logout'),  # ログアウトURLパターンを追加
        path('activate/<uidb64>/<token>/', views.activate, name='activate'),#メール認証用
    path('restaurants/<int:restaurant_id>/reserve/', make_reservation, name='make_reservation'),
    path('reservations/', reservation_list, name='reservation_list'),
    path('reservations/<int:reservation_id>/cancel/', cancel_reservation, name='cancel_reservation'),
]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)