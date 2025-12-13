from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Product, Variation
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


##  - View Function that handles http requests.
def product_details(request, category_slug, product_slug):

    try:
        ##  - Query the product.
        #   - Product.objects: Manager(Interface to database),  - .get(): Return one object or raises exception.
        #   - category__slug: Foreign key traversal (follows the relationship from Product -> Category)
        #
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )

        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()

        # ### - Sol 1) Filter by product (Good)
        # ##  - variation_set: Reverse ForeignKey Relationship
        # #   - We give 'related_name' prop to 'product' field in 'Variation' model, so instead of 'variation_set' we use just 'variations'
        # colors = single_product.variations.filter(
        #     variation_category="color", is_active=True
        # )

        # sizes = single_product.variations.filter(
        #     variation_category="size", is_active=True
        # )

        # ### - Sol 2) Use manager with filter (Good)
        # ##  - This will little a bit Slow the app due to multiple queries to database.
        # ##  - We use variations manager for colors and sizes, so instead of getting them manually
        # #   we can get directly. i.e,
        # colors = Variation.objects.colors().filter(product=single_product)
        # sizes = Variation.objects.sizes().filter(product=single_product)

        ##  - Sol 3) Single Query (Best! ⭐)
        all_variations = single_product.variations.filter(is_active=True)
        colors = [v for v in all_variations if v.variation_category == "color"]
        sizes = [v for v in all_variations if v.variation_category == "size"]

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


##------------------------------------------ Explain Code Concepts Used in this file. -------------------------------------------------##

##  - ⭐ variation_set: Reverse ForeignKey Relationship
#            colors = single_product.variation_set.filter(
#                 variation_category="color", is_active=True
#             )

#   - In our models:
#   Product: has product_name, ...other_fields.
#   Variation: has product(ForeignKey), variation_categry, ...others

#   - Django Autometically creates 'variation_set'.
#       - Since 'Variation' has a foreignKey to 'Product', Django creates 'product.variation_set'.
#       - Pattern:  {related_model_lowecase}_set.

#   - ** Visual Representation **
# Product (id=1, name="Puma Shoes")
#     __ variations_set.all()
#           __ Variation(category='color', value='red')
#           __ Variation(category='color', value='blue')
#           __ Variation(category='size', value='M')
#           __ Variation(category='size', value='L')
