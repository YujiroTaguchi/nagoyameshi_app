from django.contrib import admin
from .models import Restaurant #レストラン登録のためのモデルインポート


#画面登録
class RestaurantAdmin(admin.ModelAdmin):
     list_display = ('id', 'name', 'price','img')
     search_fields = ('name',)

     def image(self, obj):
         return mark_safe('<img src="{}" style="width:100px height:auto;">'.format(obj.img.url))

admin.site.register(Restaurant,RestaurantAdmin) 