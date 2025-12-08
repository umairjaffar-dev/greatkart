from django.db import models
from django.urls import reverse

# Create model for category which includes fields like, name, image, slug, description
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=255, blank=True) ## blank=True indicate this field is optional.
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='photos/categories', blank=True)
    
    # Correct model name in DB.
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
  
#   Make string representation of model:
    def __str__(self):
        return self.category_name

    def get_url(self):
            return reverse('products_by_category', args=[self.slug])