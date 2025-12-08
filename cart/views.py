from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from store.models import Product
from .models import Cart, CartItem


def _cart_id(request):
    cart = request.session.session_key
    
    if not cart:
        cart = request.session.create
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id) # get the single product.
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))   
    cart.save()
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        cart_item.save()
        
    return redirect('cart')


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
        
    return redirect('cart')


def delete_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
    except ObjectDoesNotExist:
        pass
        
    return redirect('cart')


# Create your Cart views here.
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart        = Cart.objects.get(cart_id=_cart_id(request))
        cart_items  = CartItem.objects.filter(cart=cart, is_active=True)
        cart_items_count = cart_items.count()
        
        
        for item in cart_items:
            total += (item.product.price * item.quantity)
            quantity += 1
        tax     = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass ## Just Ignore
        
    context = {
        'total'         :total,
        'quantity'      :quantity,
        'cart_items'    :cart_items,
        'tax'           :tax,
        'grand_total'   :grand_total,
        'cart_items_count': cart_items_count
    }
    return render(request, 'cart.html', context)
