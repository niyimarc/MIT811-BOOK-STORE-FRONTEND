from django.urls import path
from .views import (
    home, 
    shop,
    product_details,
    )

app_name = 'store'
urlpatterns = [
    path('', home, name='home'),
    path('shop/', shop, name='shop'),
    path('product/<str:slug>/', product_details, name='product_detail'),
]
