from django.contrib import admin

from .models import Cart, CartItem

# Register your models here.
##  - To view Cart and CartItem models in admin tables must register your models here.
admin.site.register(Cart)
admin.site.register(CartItem)
