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
            print(categories)
        except Exception as e:
            categories = []
            print("Error fetching categories:", e)

    return {"categories": categories}

