from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Product, variation_category_choices
from category.models import Category

from cart.models import CartItem
from cart.views import _cart_id


# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 2)  ## Get only 2 product in one page.
        page_number = request.GET.get("page")
        page_products = paginator.get_page(page_number)
        products_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True).order_by("id")
        paginator = Paginator(products, 3)  ## Get only 3 product in one page.
        page_number = request.GET.get("page")
        page_products = paginator.get_page(page_number)
        products_count = products.count()

    context = {
        "products": page_products,
        "products_count": products_count,
    }

    return render(request, "store.html", context)


def product_details(request, category_slug, product_slug):

    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()

        colors = single_product.variation_set.filter(
            variation_category="color", is_active=True
        )
        sizes = single_product.variation_set.filter(
            variation_category="size", is_active=True
        )

        print("--------------------------------------- COLOR:", colors)
        print("--------------------------------------- SIZES:", sizes)

    except Exception as e:
        raise e

    context = {
        "single_product": single_product,
        "in_cart": in_cart,
        "colors": colors,
        "sizes": sizes,
    }

    return render(request, "product_details.html", context)


def search(request):
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]

        products = Product.objects.all()

        if keyword:
            products = products.filter(
                Q(product_name__icontains=keyword) | Q(description__icontains=keyword)
            ).order_by("-created_at")

    context = {
        "products": products,
        "products_count": products.count(),
    }

    return render(request, "store.html", context)
