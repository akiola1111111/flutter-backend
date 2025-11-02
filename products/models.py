from django.db import models
from authentication.models import User
import uuid
import os

def product_image_upload_path(instance, filename):
    """Generate upload path for product images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('product_images', filename)

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('grains', 'Grains'),
        ('livestock', 'Livestock'),
        ('dairy', 'Dairy'),
        ('other', 'Other'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.CharField(max_length=100)
    image = models.ImageField(upload_to=product_image_upload_path, null=True, blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=200, blank=True)  # ADD THIS FIELD
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.farmer.username}"

    class Meta:
        ordering = ['-created_at']

class ProductImage(models.Model):
    """Model for storing multiple images per product"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
    
    def __str__(self):
        return f"Image for {self.product.name}"