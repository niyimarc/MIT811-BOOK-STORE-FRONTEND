from django.urls import path
from .views import (
    add_to_cart_view, 
    get_cart_view, 
    cart, 
    delete_cart_item_view, 
    checkout,
    )

app_name = 'cart'
urlpatterns = [
    path('cart/', cart, name='cart'),
    path('add_to_cart/', add_to_cart_view, name='add_to_cart'),
    path('get_cart/', get_cart_view, name='get_cart'),
    path('remove_cart/<int:product_id>/', delete_cart_item_view, name='delete_cart_item'),
    path('checkout/', checkout, name='checkout'),
]
