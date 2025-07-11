from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
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
    price = models.IntegerField(default=0)
    discount = models.IntegerField(default=0, validators=PERCENTAGE_VALIDATOR)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_final_price(self):
        return self.price * (1 - self.discount / 100)

    def __str__(self):
        return self.slug


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField(Product, related_name="wishlisted_by")

    def __str__(self):
        return f"{self.user.username}'s wishlist"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="cart" , null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.cart_items.all())
    def item_count(self):
        return self.cart_items.count()

    def __str__(self):
        return f"{self.user.username}'s cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def total_price(self):
        return self.product.get_final_price() * self.quantity

    def __str__(self):
        return f"{self.product.name_en} x {self.quantity}"

class Tier(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='tiers')
    points_required = models.PositiveIntegerField()
    discount_percent = models.PositiveIntegerField()

    class Meta:
        ordering = ['points_required']  # So we can pick the highest matched tier

    def __str__(self):
        return f"{self.brand.name} - {self.discount_percent}% @ {self.points_required} pts"


class UserBrandPoints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'brand')

    def __str__(self):
        return f"{self.user.username} - {self.brand.name} - {self.points} pts"


