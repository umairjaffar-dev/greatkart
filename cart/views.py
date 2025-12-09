from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from store.models import Product
from .models import Cart, CartItem


def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()
    return cart


##  - ✅ Helper Function: _cart_id()

##  - ⭐ What it does:
#       - Gets or Create a unique identifier for the visitor cart.
#       - Uses Django's session system to track anonymous users.

##  - ⭐ How it work:
#       - get or create a session Key as unique Id for browser session and return that session key to use as cart_id.

##  - ⭐ Session Core Concept:
#       - Session let Django remember users b/w page visits.
#       - Like a temporary memory that lasts until browser closes.
#       - Each visitor get a unique session ID stored in a cookie.


def add_cart(request, product_id):
    ##  - Get the product from database.
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect("shop")

    ##  - Get cart if cart exists in database with same session id that make requests.
    #   - else create a cart with unique car_id (cari_id=request.session.session_key)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    ## Get or create CartItem from database.
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        cart_item.save()

    return redirect("cart")


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except ObjectDoesNotExist:
        pass

    return redirect("cart")


def delete_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
    except ObjectDoesNotExist:
        pass

    return redirect("cart")


# Create your Cart views here.
def cart(request, total=0, quantity=0, cart_items=None):
    cart_items_count = 0
    tax = 0
    grand_total = 0

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity

        cart_items_count = cart_items.count()
        tax = (2 * total) / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        cart_items = []
        pass  ## Just Ignore

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
        "cart_items_count": cart_items_count,
    }
    return render(request, "cart.html", context)
