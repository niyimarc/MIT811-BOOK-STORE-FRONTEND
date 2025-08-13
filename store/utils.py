from django.urls import reverse
from urllib.parse import urlencode
import requests
from functools import wraps
from django.shortcuts import redirect

def get_products(
        page=1, 
        search="", 
        order_by=None, 
        categories=None, 
        format_type=None, 
        stock_status=None,
        rating=None,
        min_price=None,
        max_price=None
        ):
    order_by = order_by or []
    categories = categories or []

    endpoint = "/api/catalog/books/"
    params = {
        "endpoint_type": "public",
        "page": page,
    }

    if search:
        params["search"] = search

    if order_by:
        params["order_by"] = order_by if isinstance(order_by, list) else [order_by]

    if categories:
        params["categories"] = categories if isinstance(categories, list) else [categories]

    if format_type:
        params["format_type"] = format_type

    if stock_status:
        params["stock_status"] = stock_status

    if rating is not None:
        params["rating_below"] = rating

    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price

    query_string = urlencode(params, doseq=True)  # doseq handles multiple values

    return reverse("proxy_handler") + f"?endpoint={endpoint}&{query_string}"

def get_rating_counts():
    endpoint = "/api/catalog/rating-counts/"
    params = {
        "endpoint_type": "public",
    }
    query_string = urlencode(params, doseq=True)
    return reverse("proxy_handler") + f"?endpoint={endpoint}&{query_string}"

def remove_params(querydict, *params):
    qs = querydict.copy()
    for p in params:
        qs.pop(p, None)
    return qs.urlencode()


def get_cart_data(request):
    access_token = request.session.get('access_token')
    cart_items = []
    guest = False

    if access_token:
        proxy_url = request.build_absolute_uri(
            reverse('proxy_handler') + '?endpoint=/store/api/cart/get_user_cart/&endpoint_type=private'
        )
        sessionid = request.COOKIES.get('sessionid')

        try:
            response = requests.get(
                proxy_url,
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Cookie': f'sessionid={sessionid}'
                }
            )
            if response.status_code == 200:
                cart_items = response.json().get('cart_items', [])
        except Exception as e:
            print("Error fetching authenticated cart:", e)

    else:
        # Guest user cart via proxy using public endpoint
        guest_cart = request.session.get('cart', [])
        guest = True

        if guest_cart:
            proxy_url = request.build_absolute_uri(
                reverse('proxy_handler') + '?endpoint=/store/api/cart/guest_cart_details/&endpoint_type=public'
            )
            try:
                response = requests.post(
                    proxy_url,
                    json={'cart_items': guest_cart}
                )
                if response.status_code == 200:
                    cart_items = response.json()
            except Exception as e:
                print("Error fetching guest cart via proxy:", e)

    cart_count = sum(item.get('quantity', 0) for item in cart_items)

    # Sum total price
    cart_total = sum(item.get('get_total_price', 0) for item in cart_items)
    return {
        'cart_items': cart_items,
        'cart_count': cart_count,
        'cart_total': cart_total,
        'guest': guest
    }

def cart_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        cart_data = get_cart_data(request)
        if not cart_data.get('cart_items'):
            return redirect('store:shop')
        return view_func(request, *args, **kwargs)
    return wrapper

def submit_billing_address(request, data):
    access_token = request.session.get("access_token")
    if not access_token:
        return {'success': False, 'error': 'Unauthorized'}

    user_profile = request.session.get("user_profile", {})
    billing_address = user_profile.get("billing_address")

    if billing_address and billing_address.get("is_verified"):
        return {'success': True, 'skipped': True}

    endpoint = "/api/user/billing_address/"
    billing_url = request.build_absolute_uri(
        reverse('proxy_handler') + f"?endpoint={endpoint}&endpoint_type=private"
    )
    sessionid = request.COOKIES.get("sessionid")

    try:
        response = requests.post(
            billing_url,
            json=data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Cookie": f"sessionid={sessionid}"
            }
        )
        if response.status_code in (200, 201):
            # Update session with latest user profile
            profile_url = request.build_absolute_uri(
                reverse('proxy_handler') + "?endpoint=/api/user/profile/&endpoint_type=private"
            )
            profile_response = requests.get(
                profile_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Cookie": f"sessionid={sessionid}"
                }
            )
            if profile_response.status_code == 200:
                request.session["user_profile"] = profile_response.json()

            return {'success': True}
        return {'success': False, 'error': response.text}
    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}

def create_order(request, shipping_data, note, cart_items):
    access_token = request.session.get("access_token")
    if not access_token:
        return {'success': False, 'error': 'Unauthorized'}

    endpoint = "/store/api/orders/create/"
    order_url = request.build_absolute_uri(
        reverse('proxy_handler') + f"?endpoint={endpoint}&endpoint_type=private"
    )

    sessionid = request.COOKIES.get("sessionid")

    # Convert cart_items into order_items payload
    order_items = []
    for item in cart_items:
        order_items.append({
            "product": item["product_id"],
            "quantity": item["quantity"]
        })

    payload = {
        "note": note,
        "shipping_address": {
            "address": shipping_data.get("shipping_address"),
            "apartment": shipping_data.get("shipping_apartment"),
            "city": shipping_data.get("shipping_city"),
            "state": shipping_data.get("shipping_state"),
            "country": shipping_data.get("shipping_country"),
            "zip_code": shipping_data.get("shipping_zip"),
        },
        "order_items": order_items
    }

    try:
        response = requests.post(
            order_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Cookie": f"sessionid={sessionid}"
            }
        )
        if response.status_code in (200, 201):
            return {"success": True}
        return {"success": False, "error": response.text}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}
