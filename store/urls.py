from django.urls import path
from .views import (
    home, 
    shop,
    )

app_name = 'store'
urlpatterns = [
    path('', home, name='home'),
    path('shop/', shop, name='shop'),
]
