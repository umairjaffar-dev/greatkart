from .models import Cart, CartItem

from .views import _cart_id


##  - Make a cart_counter context_processor to show the shopping cart count value in the project.
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
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Count all active items in cart
        cart_items_count = cart_items.count()

    except Cart.DoesNotExist:
        cart_items_count = 0

    return {"cart_items_count": cart_items_count}
