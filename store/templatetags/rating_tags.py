from django import template
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

register = template.Library()

@register.filter
def rating_to_star_template(rating):
    """
    Converts a float rating into a star HTML template path.
    Falls back to 0_star.html if template is missing or rating invalid.
    """
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0

    # Determine star count based on rating range
    if rating == 0:
        star_file = "0_star.html"
    elif rating < 1.5:
        star_file = "1_star.html"
    elif rating < 2.5:
        star_file = "2_star.html"
    elif rating < 3.5:
        star_file = "3_star.html"
    elif rating < 4.5:
        star_file = "4_star.html"
    else:
        star_file = "5_star.html"

    path = f"rating_star/{star_file}"

    # Check if template exists, otherwise fallback
    try:
        get_template(path)
        return path
    except TemplateDoesNotExist:
        return "rating_star/0_star.html"
