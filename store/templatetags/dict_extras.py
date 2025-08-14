from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(int(key)) if d else 0

@register.filter
def split(value, delimiter=" "):
    """Splits a string into a list based on the delimiter."""
    return value.split(delimiter)