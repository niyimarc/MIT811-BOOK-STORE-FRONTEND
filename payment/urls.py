from django.urls import path
from .views import (
    payment_view
    )

app_name = 'payment'
urlpatterns = [
    path("payment/<str:order_reference>/<str:payment_method>/", payment_view, name="payment_view"),

]
