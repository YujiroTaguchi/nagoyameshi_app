from django.shortcuts import render
from django.views.generic import ListView
from .models import Restaurant

# トップページ用（レストランリスト）のビュー
class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'restaurant_list.html'
    context_object_name = 'restaurants'
