from django.db import models
from django.urls import reverse

from category.models import Category


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)

    ##  - Whenever we delete the category all the products of category will also be deleted
    ##  because here category is foreignKey.
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse("product_details", args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


##  ✅ Key Fields Explained:
##  - ⭐ slug:  URL-friendly version of the product name (i.e., "red-shoes" instead of "Red Shoes")

##  ✅ Props inside fields:
#   - blank=True:   Field is optional in forms.
#   - unique=True:  No product can have the same name i.e, product_name and slug.
#   - ForeignKey:   Links product to category tabel (many-to-one relationship: one category have many products).
#   - on_delete=models.CASCADE:  If category is deleted, all its products are deleted too.
#   - auto_now_add=True     Auto sets products date when product is created.
#   - auto_now=True     Updates date whenever product is modified.


##  - 1) Working on managers.
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

variation_category_choices = (
    ('color', 'color'),
    ('size', 'size'),
)
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=255, choices=variation_category_choices)
    variation_value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = VariationManager()
    
    def __str__(self):
        return self.variation_value