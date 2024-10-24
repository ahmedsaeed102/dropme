from datetime import date
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]

class Category(models.Model):
    category_name = models.CharField(max_length=50, default="Muqbis")
    img = models.ImageField(upload_to="marketplace/categories", blank=True, null=True)

    def __str__(self) -> str:
        return self.category_name

class Product(models.Model):
    product_id = models.IntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=100)
    description_en = models.TextField()
    description_ar = models.TextField()
    img = models.ImageField(upload_to="marketplace/products")
    product_page_link = models.URLField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.IntegerField(default=0, validators=PERCENTAGE_VALIDATOR)
    price_after_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_points = models.PositiveIntegerField(default=0)
    coupon = models.CharField(max_length=20, default="DropMe")
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.product_name

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField(Product, related_name="wishlisted_by")

    def __str__(self):
        return f"{self.user.username}'s wishlist"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    count = models.PositiveIntegerField(default=0)
    total = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.username

class Entry(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.product.product_name + " | " + str(self.quantity)

class SpecialOffer(models.Model):
    description = models.TextField(blank=True, null=True)
    required_points = models.PositiveBigIntegerField()
    reward_points = models.PositiveBigIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)

    @property
    def is_ongoing(self) -> bool:
        return self.end_date >= date.today()

class UserOffer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_offers")
    offer = models.ForeignKey(SpecialOffer, on_delete=models.CASCADE, related_name="offer_status")
    can_be_used = models.BooleanField(default=True)
    remaining_amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.email} | {self.offer.id} | {self.remaining_amount}"