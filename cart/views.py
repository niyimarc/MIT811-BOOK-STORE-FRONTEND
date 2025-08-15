import requests
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
import json
from django.views.decorators.http import require_GET
from .utils import (
    get_cart_data, 
    cart_required, 
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