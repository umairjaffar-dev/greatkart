from django.db import models

from store.models import Product, Variation
from accounts.models import Account

# Create your models here.
class Cart(models.Model):
    cart_id     = models.CharField(max_length=255, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id
    
    
class CartItem(models.Model):
    user        = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations  = models.ManyToManyField(Variation, blank=True)
    cart        = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity    = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def sub_total(self): ## - Custom method to calculate item cost (price * quantity)
        return self.product.price * self.quantity
    
    def __str__(self):
        return self.product.product_name
    
##  - ✅ - Model Fields Explaination:
#   - product:  Which 'Product' is in the 'CartItem' Model.
#   - cart:     Which 'Cart' this 'CartItem' belong to.
##  - Relationship: Cart(1) ----> (Many) CartItem (Many) ----> (1) Product
    
