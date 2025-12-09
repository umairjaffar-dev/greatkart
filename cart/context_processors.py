from .models import Cart, CartItem

from .views import _cart_id


def cart_counter(request):
    """
    This function runs on EVERY page request
    Makes cart_items_count available everywhere
    """

    if "admin" in request.path:
        return {}

    try:
        # Get current user's cart using session ID
        cart = Cart.objects.get(cart_id=_cart_id(request))

        # Count all active items in cart
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        cart_items_count = cart_items.count()

    except Cart.DoesNotExist:
        cart_items_count = 0

    return {"cart_items_count": cart_items_count}
