# urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

from nagoyameshi.views import (
    signup,
    login_view,
    activate,
    RestaurantDetailView,
    RestaurantListView,
    make_reservation,
    reservation_list,
    cancel_reservation,
    add_to_favorites,
    remove_from_favorites,
    favorite_list,
    mypage,
    edit_profile,
    CreateCheckoutSessionView,
    SuccessView,
    CancelView,
    reservation_success,
    cancel_subscription,
    add_review, edit_review, delete_review,
    create_billing_portal_session,
    subscription_required_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('restaurants/', RestaurantListView.as_view(), name='restaurant_list'),
    path('restaurants/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='restaurant_list'), name='logout'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('restaurants/<int:restaurant_id>/reserve/', make_reservation, name='make_reservation'),
    path('reservations/', reservation_list, name='reservation_list'),
    path('reservations/<int:reservation_id>/cancel/', cancel_reservation, name='cancel_reservation'),
    path('restaurants/<int:restaurant_id>/add_to_favorites/', add_to_favorites, name='add_to_favorites'),
    path('favorites/<int:favorite_id>/remove/', remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', favorite_list, name='favorite_list'),
    path('mypage/', mypage, name='mypage'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'), 
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('reservation_success/<int:reservation_id>/', reservation_success, name='reservation_success'),
    path('cancel-subscription/', cancel_subscription, name='cancel_subscription'),
    path('restaurants/<int:restaurant_id>/review/add/', add_review, name='add_review'),
    path('reviews/<int:review_id>/edit/', edit_review, name='edit_review'),
    path('reviews/<int:review_id>/delete/', delete_review, name='delete_review'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('billing-portal/', create_billing_portal_session, name='create_billing_portal_session'),
    path('subscription-required/', subscription_required_view, name='subscription_required'),  # エラーページのURLパターン
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
