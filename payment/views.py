from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseNotFound
from auth_app.utils import session_access_required
from django.conf import settings
from .utils import get_payment_verification, get_order_details
import requests

# Create your views here.
@session_access_required
def payment_view(request, order_reference, payment_method):
    # Grab the payment reference or transaction_id from query params
    ref_or_tx = request.GET.get("reference") or request.GET.get("transaction_id")

    # Get order details
    order = get_order_details(request, order_reference)
    # print(order)
    if not order or "id" not in order:
        return HttpResponseNotFound("Order not found")

    if order.get("payment_made"):
        return redirect("store:shop")

    order_id = order["id"]

    verification_result = None
    if ref_or_tx:  # Only verify if frontend callback included a reference/transaction_id
        verification_result = get_payment_verification(
            request, order_id, payment_method, reference=ref_or_tx
        )

        # Redirect if verification was successful
        if verification_result and verification_result.get("success"):
            return redirect("store:shop")

    context = {
        "order": order,
        "order_id": order_id,
        "order_reference": order_reference,
        "payment_method": payment_method,
        "reference": ref_or_tx,
        "verification_result": verification_result,
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY,
        "FLUTTERWAVE_PUBLIC_KEY": settings.FLUTTERWAVE_PUBLIC_KEY,
        "INTERSWITCH_MERCHANT_CODE": settings.INTERSWITCH_MERCHANT_CODE,
        "INTERSWITCH_PAY_ITEM_ID": settings.INTERSWITCH_PAY_ITEM_ID,
    }

    return render(request, "payment.html", context)
