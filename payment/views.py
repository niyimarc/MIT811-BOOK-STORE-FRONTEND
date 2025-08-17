from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseNotFound
from auth_app.utils import session_access_required
from django.conf import settings
from .utils import get_payment_verification, get_order_details
import requests

# Create your views here.
@session_access_required
def payment_view(request, order_reference, payment_method):
    reference = request.GET.get("reference")

    # Fetch the updated order from the backend via proxy handler
    order = get_order_details(request, order_reference)

    # Check if order exists
    if not order or "id" not in order:
        return HttpResponseNotFound("Order not found")

    # print(order)
    order_id = order["id"]
    # print(f"Order ID: {order_id}")
    proxy_url, proxy_headers = get_payment_verification(request, order_id, payment_method, reference)

    context = {
        "order": order,
        "order_id": order_id, # used by paystack
        "order_reference": order_reference,
        "payment_method": payment_method,
        "reference": reference,
        "proxy_url": proxy_url,
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY,
        "FLUTTERWAVE_PUBLIC_KEY": settings.FLUTTERWAVE_PUBLIC_KEY,
        "INTERSWITCH_MERCHANT_CODE": settings.INTERSWITCH_MERCHANT_CODE,
        "INTERSWITCH_PAY_ITEM_ID": settings.INTERSWITCH_PAY_ITEM_ID,
    }
    return render(request, "payment.html", context)