from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Restaurant, CustomUser, Category, Review, Reservation, Favorite  # レストラン登録、サインアップ等各モデルインポート
from django.utils.safestring import mark_safe

# レストラン登録
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'img_display')  # img_displayを追加
    search_fields = ('name', )  # categoryでの検索を追加

    def img_display(self, obj):
        if obj.img:
            return mark_safe('<img src="{}" style="width:100px; height:auto;">'.format(obj.img.url))
        return ""
    img_display.short_description = 'Image'  # 管理画面での列名を設定

# カスタムユーザーモデルの管理画面登録
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'is_active', 'is_end_user', 'is_admin_user', 'is_subscription_user', 'stripe_subscription_id')
    search_fields = ('email', 'full_name')
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'furigana', 'postal_code', 'address', 'phone_number', 'birthdate', 'occupation')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_end_user', 'is_admin_user', 'is_subscription_user', 'stripe_subscription_id', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'furigana', 'postal_code', 'address', 'phone_number', 'birthdate', 'occupation', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)

# カテゴリーの管理
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# レビューの管理
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'user', 'rating', 'comment', 'created_at')
    search_fields = ('restaurant__name', 'user__email', 'rating')


# 予約の管理
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'user', 'reservation_date', 'reservation_time', 'number_of_people')
    search_fields = ('restaurant__name', 'user__email', 'reservation_date', 'reservation_time')

# お気に入りの管理
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant')
    search_fields = ('user__email', 'restaurant__name')


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Reservation, ReservationAdmin)  # ReservationAdminを登録
admin.site.register(Favorite, FavoriteAdmin)
