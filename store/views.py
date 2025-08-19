from django.shortcuts import render, redirect
from .utils import get_products, remove_params, get_rating_counts, get_product_details, submit_product_rating, submit_contact_form
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse, Http404
import requests
from django.contrib import messages
import math

# Create your views here.
def home(request):
    context = {

    }
    return render(request, 'home.html', context)

def shop(request):
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    search = request.GET.get("search", "")
    order_by = request.GET.getlist("order_by")
    selected_categories = request.GET.getlist("categories")
    selected_format = request.GET.get("format_type")
    selected_stock_status = request.GET.get("stock_status")

    try:
        selected_rating = int(request.GET.get("rating", "")) if request.GET.get("rating") else None
    except ValueError:
        selected_rating = None

    try:
        min_price = float(request.GET.get("min_price", "")) if request.GET.get("min_price") else None
    except ValueError:
        min_price = None

    try:
        max_price = float(request.GET.get("max_price", "")) if request.GET.get("max_price") else None
    except ValueError:
        max_price = None

    # Build proxy URL
    proxy_url = request.build_absolute_uri(
        get_products(
            page=page, 
            search=search, 
            order_by=order_by, 
            categories=selected_categories, 
            format_type=selected_format, 
            stock_status=selected_stock_status,
            rating=selected_rating,
            min_price=min_price,
            max_price=max_price
        )
    )

    try:
        response = requests.get(proxy_url, timeout=10)
        response.raise_for_status()
        products_data = response.json()
    except requests.RequestException as e:
        products_data = {"results": [], "count": 0, "next": None, "previous": None}

    # Fetch rating counts for filter sidebar
    rating_counts_url = request.build_absolute_uri(get_rating_counts())
    try:
        rating_response = requests.get(rating_counts_url, timeout=10)
        rating_response.raise_for_status()
        ratings_data = rating_response.json()  # [{"rating": 1, "product_count": 7}, ...]
        # print(ratings_data)
    except requests.RequestException:
        ratings_data = []
    # Has prev/next from API
    has_prev = bool(products_data.get("previous"))
    has_next = bool(products_data.get("next"))

    # Get total pages from API count
    total_products = products_data.get("count", 0)
    per_page = len(products_data.get("results", [])) or 1  # avoid division by zero
    total_pages = math.ceil(total_products / per_page)

    # Build page number list
    if has_prev and has_next:
        page_numbers = [page - 1, page, page + 1]
    elif has_prev and not has_next:
        start = max(1, page - 2)
        page_numbers = [p for p in [start, start + 1, start + 2] if p <= page]
    elif not has_prev and has_next:
        page_numbers = [page, page + 1, page + 2]
    else:
        page_numbers = [page]

    # Remove pages that don't exist
    page_numbers = [p for p in page_numbers if p <= total_pages]

    # Show ellipsis only if there are more pages after the last number
    show_ellipsis = bool(page_numbers) and total_pages > page_numbers[-1]

    qs = request.GET.copy()
    qs.pop("page", None)
    qs_str = qs.urlencode()

    qs_no_format_str = remove_params(request.GET, "format_type", "page")
    qs_no_stock_str = remove_params(request.GET, "stock_status", "page")

    context = {
        "products": products_data.get("results", []),
        "total": total_products,
        "page": page,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1 if has_prev and page > 1 else None,
        "next_page": page + 1 if has_next else None,
        "page_numbers": page_numbers,
        "show_ellipsis": show_ellipsis,
        "qs": qs_str,
        "qs_no_format": qs_no_format_str,
        "qs_no_stock": qs_no_stock_str,
        "search": search,
        "order_by": order_by,
        "selected_categories": selected_categories,
        "selected_format": selected_format,
        "selected_stock_status": selected_stock_status,
        "selected_rating": selected_rating,
        "min_price": min_price,
        "max_price": max_price,
        "ratings_data": ratings_data,
    }

    # Number of items on current page
    results_on_page = len(products_data.get("results", []))

    # Calculate first and last item number
    if total_products == 0:
        first_item = 0
        last_item = 0
    else:
        first_item = (page - 1) * results_on_page + 1
        last_item = (page - 1) * results_on_page + results_on_page

    # Add to context
    context["results_range"] = {
        "first": first_item,
        "last": last_item,
        "total": total_products
    }
    return render(request, "shop.html", context)

def product_details(request, slug):
    api_url = request.build_absolute_uri(get_product_details(slug))
    rating_url = request.build_absolute_uri(submit_product_rating(slug))

    if request.method == "POST":
        score = request.POST.get("score")
        review = request.POST.get("review")

        headers = {
            "Authorization": f"Bearer {request.session.get('access_token')}",
            "Content-Type": "application/json",
        }
        payload = {
            "score": int(score) if score else None,
            "review": review
        }

        try:
            res = requests.post(rating_url, json=payload, headers=headers, timeout=10)
            if res.status_code in (200, 201):
                messages.success(request, "Review submitted successfully!")
            else:
                messages.error(request, f"Error submitting review: {res.text}")
        except requests.RequestException:
            messages.error(request, "Could not submit review. Please try again later.")

        return redirect("store:product_detail", slug=slug)


    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        product_data = response.json()
    except requests.RequestException:
        product_data = None
    # print(product_data)
    context = {
        "product": product_data,
        "rating_url": rating_url
    }

    return render(request, "product_details.html", context)

def contact(request):
    submit_contact_form_url = request.build_absolute_uri(submit_contact_form())
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        payload = {
                "name": name,
                "email": email,
                "subject": subject,
                "message": message
            }
        try:
            res = requests.post(submit_contact_form_url, json=payload, timeout=10)
            if res.status_code in (200, 201):
                messages.success(request, "Message submitted successfully!")
                return redirect("store:contact")
            else:
                messages.error(request, f"Error submitting message: {res.text}")
                return redirect("store:contact")
        except requests.RequestException:
            messages.error(request, "Could not submit message. Please try again later.")
            return redirect("store:contact")

    context = {

    }
    return render(request, 'contact.html', context)

def about(request):
    context = {

    }
    return render(request, 'about.html', context)