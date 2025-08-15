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

def get_product_details(slug):
    endpoint = f"/api/catalog/books/{slug}/"
    params = {
        "endpoint_type": "public",
    }
    query_string = urlencode(params, doseq=True)
    return reverse("proxy_handler") + f"?endpoint={endpoint}&{query_string}"

def submit_product_rating(slug):
    endpoint = f"/api/catalog/{slug}/reviews/"
    params = {
        "endpoint_type": "private",
    }
    query_string = urlencode(params, doseq=True)
    return reverse("proxy_handler") + f"?endpoint={endpoint}&{query_string}"

def remove_params(querydict, *params):
    qs = querydict.copy()
    for p in params:
        qs.pop(p, None)
    return qs.urlencode()