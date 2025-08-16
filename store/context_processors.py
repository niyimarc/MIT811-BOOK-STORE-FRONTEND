from django.conf import settings
import requests
from django.urls import reverse
from django.core.cache import cache

def app_information(request):
    return {
        "business_name": settings.BUSINESS_NAME,
        "business_logo": settings.BUSINESS_LOGO,
        "contact_email": settings.CONTACT_EMAIL,
    }

def categories_data(request):
    categories = cache.get("categories_data")
    if not categories:
        try:
            resp = requests.get(
                request.build_absolute_uri("/proxy/"),
                params={
                    "endpoint": "/api/catalog/categories/",
                    "endpoint_type": "public"
                },
                timeout=5
            )
            resp.raise_for_status()
            categories = resp.json()  # <-- IMPORTANT: get actual data, not just URL
            cache.set("categories_data", categories, 60 * 30)  # cache for 30 minutes
            # print(categories)
        except Exception as e:
            categories = []
            print("Error fetching categories:", e)

    return {"categories": categories}

def featured_products(request):
    cache.delete('featured_products')
    featured_products = cache.get("featured_products")
    if not featured_products:
        try:
            resp = requests.get(
                request.build_absolute_uri("/proxy/"),
                params={
                    "endpoint": "/api/catalog/featured/",
                    "endpoint_type": "public"
                },
                timeout=5
            )
            resp.raise_for_status()
            featured_products = resp.json()  # <-- IMPORTANT: get actual data, not just URL
            cache.set("featured_products", featured_products, 60 * 30)
            # print(categories)
        except Exception as e:
            featured_products = []
            print("Error fetching featured products:", e)

    return {"featured_products": featured_products}

