# from datetime import date
# from django.db import models
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.contrib.auth import get_user_model

# User = get_user_model()

# PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     img = models.ImageField(upload_to="marketplace/products")
#     link = models.URLField()

#     price_points = models.PositiveIntegerField(default=0)
#     price_eg = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
#     discount = models.IntegerField(default=0, validators=PERCENTAGE_VALIDATOR)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class PromoCode(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     code = models.CharField(max_length=20)


# class Cart(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
#     count = models.PositiveIntegerField(default=0)
#     total = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class Entry(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)


# class SpecialOffer(models.Model):
#     description = models.TextField()

#     points = models.PositiveBigIntegerField(default=0)
#     reward = models.PositiveBigIntegerField(default=0)

#     start_date = models.DateField()
#     end_date = models.DateTimeField()

#     created_at = models.DateTimeField(auto_now_add=True)

#     @property
#     def is_ongoing(self) -> bool:
#         return self.end_date > date.today()
