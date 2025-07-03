from datetime import date
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug

class Brand(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Brand.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug

class Product(models.Model):
    name_en = models.CharField(max_length=200, blank=False, null=False)
    name_ar = models.CharField(max_length=200, blank=False, null=False)
    description_en = models.TextField()
    description_ar = models.TextField()
    img_urls = models.JSONField(default=list)
    product_page_link = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.IntegerField(default=0, validators=PERCENTAGE_VALIDATOR)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.slug

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField(Product, related_name="wishlisted_by")

    def __str__(self):
        return f"{self.user.username}'s wishlist"






















# class Cart(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
#     count = models.PositiveIntegerField(default=0)
#     total = models.IntegerField(default=0)
#     active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self) -> str:
#         return self.user.username
#
# class Entry(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
#     quantity = models.PositiveIntegerField(default=1)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self) -> str:
#         return self.product.product_name + " | " + str(self.quantity)