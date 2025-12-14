from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from store.models import Product, Variation
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


##  - 2) Instead of using get request in ADD_TO_CART use post request send data into form.
def add_cart(request, product_id):
    ##  - Get the product from database.
    try:
        product = Product.objects.get(id=product_id)
        product_variations = []
    except Product.DoesNotExist:
        return redirect("shop")

    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
            # Now check that these key and values matches the db variations.
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variations.append(variation)
            except:
                pass

    ##  - Get cart if cart exists in database with same session id that make requests.
    #   - else create a cart with unique car_id (cari_id=request.session.session_key)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()
    
    ##  - To add same variation in one CartItem and for different variations we will add
    #   a new CartItem. So for that we firts filter the cartItem and check cart contain
    #   same variation or not, if found same the increase the quantity else create a new cartItem.
    
    ##  - filter cart items:
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    ## Get or create CartItem from database.
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

            if product_variations in ex_var_list:
                # Increase the quantity of the product
                index = ex_var_list.index(product_variations)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                # Create a new cart-item
                item = CartItem.objects.create(product=product, cart=cart, quantity=1)
                if len(product_variations) > 0:  ##  - Check the len of prod_variations.
                    item.variations.clear()
                    item.variations.add(*product_variations)
                item.save()
    else:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if len(product_variations) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variations)
        cart_item.save()

    return redirect("cart")


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except ObjectDoesNotExist:
        pass

    return redirect("cart")


def delete_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
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

    # print("=========== Cart Item ============", cart_items)

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
        "cart_items_count": cart_items_count,
    }
    return render(request, "cart.html", context)
