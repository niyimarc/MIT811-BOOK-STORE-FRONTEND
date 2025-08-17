from .utils import get_cart_data

def cart_context(request):
    data = get_cart_data(request)
    # print(data)
    return {
        'cart_items': data.get('cart_items', []),
        'cart_count': data.get('cart_count', 0),
        'cart_total': data.get('cart_total', 0),
        'guest_user': data.get('guest', False)
    }