# urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

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
    reservation_success
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
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('reservation_success/<int:reservation_id>/', reservation_success, name='reservation_success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
