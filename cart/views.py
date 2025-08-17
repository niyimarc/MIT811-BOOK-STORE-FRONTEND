import requests
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
import json
from django.views.decorators.http import require_GET
from auth_app.utils import session_access_required
from .utils import (
    get_cart_data, 
    cart_required,
    create_order,
    submit_billing_address, 
    )

# Create your views here.
def add_to_cart_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        # Build proxy handler URL
        proxy_url = request.build_absolute_uri(
            reverse('proxy_handler') + '?endpoint=/api/cart/add_to_cart/&endpoint_type=private'
        )

        # Prepare the payload
        payload = {
            'product_id': product_id,
            'quantity': quantity
        }

        access_token = request.session.get('access_token')
        sessionid = request.COOKIES.get('sessionid')

        # If no access token, treat user as guest and save to session
        if not access_token:
            cart = request.session.get('cart', [])
            for item in cart:
                if item['product_id'] == product_id:
                    item['quantity'] += quantity
                    break
            else:
                cart.append({'product_id': product_id, 'quantity': quantity})
            request.session['cart'] = cart
            # request.session['cart_changed'] = True
            return JsonResponse({'success': True, 'offline': True})
        
        try:

            response = requests.post(
                proxy_url,
                json=payload,
                headers={
                    # 'Authorization': f"Bearer {access_token}",
                    'Cookie': f'sessionid={sessionid}'
                }
            )

            if response.status_code == 200:
                # request.session['cart_changed'] = True
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Failed to add to cart'}, status=400)

        except requests.exceptions.RequestException:
            return JsonResponse({'error': 'Network error'}, status=500)
        
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@require_GET
def get_cart_view(request):
    data = get_cart_data(request)
    return JsonResponse(data)

@cart_required
def cart(request):
    context = {

    }
    return render(request, 'cart.html', context)

def delete_cart_item_view(request, product_id):
    if request.method != 'DELETE' and request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    access_token = request.session.get("access_token")

    if access_token:
        # Authenticated user - use proxy to call private API
        endpoint = f"/api/cart/delete_cart_item/{product_id}/"
        proxy_url = request.build_absolute_uri(
            reverse('proxy_handler') + f"?endpoint={endpoint}&endpoint_type=private"
        )

        sessionid = request.COOKIES.get('sessionid')
        try:
            response = requests.delete(
                proxy_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    'Cookie': f'sessionid={sessionid}',
                }
            )
            if response.status_code == 200:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({
                    'success': False,
                    'error': f"Failed with status {response.status_code}"
                }, status=response.status_code)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    else:
        # Guest user - modify session cart
        session_cart = request.session.get("cart", [])
        updated_cart = [item for item in session_cart if item.get("product_id") != product_id]
        request.session["cart"] = updated_cart
        return JsonResponse({'success': True})
    
@cart_required
@session_access_required
def checkout(request):
    if request.method == "POST":
        data = request.POST  # HTML form submission

        # --- Billing Data ---
        billing_data = {
            "address": data.get("billing_address"),
            "apartment": data.get("billing_apartment"),
            "nearest_bus_stop": data.get("billing_nearest_bus_stop"),
            "state": data.get("billing_state"),
            "country": data.get("billing_country"),
            "zip_code": data.get("billing_zip"),
        }

        billing_result = submit_billing_address(request, billing_data)
        if not billing_result.get("success"):
            messages.error(request, "Billing validation failed. Please check your details.")
            return render(request, "checkout.html", {
                "form_data": data,  # prefill old inputs
            })

        # --- Shipping Data ---
        use_different_shipping = data.get("different_address") == "on"

        if use_different_shipping:
            shipping_data = {
                "shipping_address": data.get("shipping_address"),
                "shipping_apartment": data.get("shipping_apartment"),
                "shipping_nearest_bus_stop": data.get("shipping_nearest_bus_stop"),
                "shipping_state": data.get("shipping_state"),
                "shipping_country": data.get("shipping_country"),
                "shipping_zip": data.get("shipping_zip"),
            }
        else:
            shipping_data = {
                "shipping_address": billing_data["address"],
                "shipping_apartment": billing_data["apartment"],
                "shipping_nearest_bus_stop": billing_data["nearest_bus_stop"],
                "shipping_state": billing_data["state"],
                "shipping_country": billing_data["country"],
                "shipping_zip": billing_data["zip_code"],
            }

        # --- Order Note ---
        order_note = {"note": data.get("order_note", "")}

        # --- Cart Items ---
        cart_data = get_cart_data(request)
        cart_items = cart_data.get("cart_items", [])

        order_result = create_order(request, shipping_data, order_note, cart_items)
        if not order_result.get("success"):
            messages.error(request, "Could not create order. Please try again.")
            return render(request, "checkout.html", {
                "form_data": data,
            })

        # --- Success: Redirect to payment ---
        order_reference = order_result.get("order_id")
        payment_method = data.get("payment_type")

        # messages.success(request, "Order created successfully! Please proceed to payment.")
        return redirect(
            "payment:payment_view",
            order_reference=order_reference,
            payment_method=payment_method
        )

    return render(request, "checkout.html", {})