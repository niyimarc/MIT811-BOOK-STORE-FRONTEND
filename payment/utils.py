from urllib.parse import urlencode
from django.urls import reverse
from django.http import Http404
import requests

def get_order_details(request, order_reference):
    endpoint = f"/api/orders/{order_reference}/"
    params = {
        "endpoint_type": "private",
    }
    url = reverse("proxy_handler") + f"?endpoint={endpoint}&{urlencode(params)}"

    # Build headers properly
    headers = {
        "Authorization": f"Bearer {request.session.get('access_token')}",
        "Cookie": f"sessionid={request.session.session_key}",
        "Content-Type": "application/json",
    }

    response = requests.get(request.build_absolute_uri(url), headers=headers)
    data = response.json()
    # print("DEBUG get_order_details response:", data)
    return data


def get_payment_verification(request, order_id, payment_method, reference=None):
    access_token = request.session.get("access_token")
    if not access_token:
        raise Http404("Unauthorized")

    sessionid = request.COOKIES.get("sessionid")
    endpoint = f"/api/payments/verify/{order_id}/{payment_method}/"
    params = {"endpoint_type": "private"}
    if reference:
        params["reference"] = reference

    url = reverse("proxy_handler") + f"?endpoint={endpoint}&{urlencode(params)}"

    headers = {"Authorization": f"Bearer {access_token}"}
    if sessionid:
        headers["Cookie"] = f"sessionid={sessionid}"

    return url, headers
