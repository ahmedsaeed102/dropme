# Marketplace APP code Doc : 

##  `models.py` Documentation

```python
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

User = get_user_model()

# Validator to ensure discount percentages are between 0 and 100
PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]
```

---

### `Category`

```python
class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
```

**Purpose:** Represents a category of products (e.g. Electronics, Clothing).
**Fields:**

* `name`: Display name for the category.
* `slug`: Unique URL-friendly identifier generated from the name.

**Custom Logic:**

```python
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
```

Auto-generates a unique slug from the `name` on save.

---

###  `Brand`

```python
class Brand(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
```

**Purpose:** Represents a brand (e.g. Nike, Samsung).
**Fields:**

* `name`: Brand name.
* `slug`: Unique slug auto-generated from the name.
* `website_url`: Optional link to brand website.

**Custom Logic:** Same slug logic as `Category`.

---

### `Product`

```python
class Product(models.Model):
    name_en = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
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
```

**Purpose:** Represents a product listed in the store.
**Key Features:**

* `name_en`, `name_ar`: Multilingual support.
* `img_urls`: Stores multiple image links as a list.
* `product_page_link`: Link to purchase page.
* `price` + `discount`: Base price and discount percentage.
* `brand`, `category`: ForeignKeys for grouping.
* `created_at`, `updated_at`: Timestamps for audit.

**Methods:**

```python
    def get_final_price(self):
        return self.price * (1 - self.discount / 100)
```

Calculates final price after applying discount.

---

### `Wishlist`

```python
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField(Product, related_name="wishlisted_by")
```

**Purpose:** Each user has one wishlist that can include many products.
**Structure:** Many-to-many relation between users and products.

---

### `Cart`

```python
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="cart", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Purpose:** Represents a shopping cart for a user.
**Features:**

* Only allows products from one brand (enforced via logic elsewhere).
* `created_at` to track session start.

**Methods:**

```python
    def total_price(self):
        return sum(item.total_price() for item in self.cart_items.all())

    def item_count(self):
        return self.cart_items.count()
```

Calculates total cart value and item count.

---

### `CartItem`

```python
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.IntegerField(default=1)
```

**Purpose:** Individual items inside a cart.
**Relation:** Each item links one cart to one product.
**Meta Logic:**

```python
    class Meta:
        unique_together = ('cart', 'product')
```

Only one entry per product per cart.

**Methods:**

```python
    def total_price(self):
        return self.product.get_final_price() * self.quantity
```

---

### `Tier`

```python
class Tier(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='tiers')
    points_required = models.PositiveIntegerField()
    discount_percent = models.PositiveIntegerField()
```

**Purpose:** Represents loyalty tiers per brand.
Example:

* Bronze (100 pts → 10%)
* Gold (200 pts → 20%)

**Meta:**

```python
    class Meta:
        ordering = ['points_required']
```

Sorted ascending by required points so highest matching tier is easily selected.

---

### `UserBrandPoints`

```python
class UserBrandPoints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
```

**Purpose:** Tracks how many points a user has per brand.
**Usage:** Used to calculate eligible tiers and checkout discounts.

**Meta:**

```python
    class Meta:
        unique_together = ('user', 'brand')
```

Each user-brand combo is unique.

---

### `Coupon`

```python
class Coupon(models.Model):
    STATUS_CHOICES = [
        ('used', 'Used'),
        ('unused', 'Unused')
    ]
    TYPE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline')
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='coupons')
    code = models.CharField(max_length=30, unique=True)
    discount = models.PositiveIntegerField()
    points_required = models.PositiveIntegerField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='online')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unused')
    created_at = models.DateTimeField(auto_now_add=True)
```

**Purpose:** Coupons can be generated or preloaded for use in checkout.
**Fields:**

* `code`: Unique identifier (string-based).
* `discount`: Discount amount or percentage.
* `type`: Online or offline use.
* `status`: Used or unused.
* `brand`: Each coupon belongs to a brand.

---

## `serializers.py` Documentation

```python
from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from .models import Product, Wishlist, Brand, Category, CartItem, Cart, UserBrandPoints, Tier
```

---

### `ProductSerializer`

```python
class ProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    brand = serializers.SlugRelatedField(slug_field='slug', queryset=Brand.objects.all())
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all())
```

**Purpose:** Serialize product details including dynamic fields like price after discount and wishlist status.

**Fields:**

* `discounted_price`: Calculated price after discount (Decimal).
* `is_wishlisted`: Checks if product is in user's wishlist (bool).
* `brand`, `category`: Uses slug instead of full nested object for cleaner responses.

**Methods:**

```python
def get_discounted_price(self, obj):
    ...
```

Calculates and returns discounted price using decimal rounding.

```python
def get_is_wishlisted(self, obj):
    ...
```

Returns True/False depending on whether the product ID is in the wishlist passed via `context`.

---

### `WishlistSerializer`

```python
class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
```

**Purpose:** Serialize a user's wishlist including full product details.

**Fields:**

* `products`: Nested list of `ProductSerializer` data (read-only).

---

### `BrandSerializer`

```python
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']
```

**Purpose:** Basic serializer for brand data.

---

### `CategorySerializer`

```python
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']
```

**Purpose:** Basic serializer for category data.

---

### `CartItemSerializer`

```python
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name_en', read_only=True)
    price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
```

**Purpose:** Serialize individual items in the cart.

**Fields:**

* `product_name`: English name of the product (read-only).
* `price`: Price after discount.
* `total_price`: Final price after quantity multiplication.

**Methods:**

```python
def get_price(self, obj):
    return obj.product.get_final_price()
```

```python
def get_total_price(self, obj):
    return obj.total_price()
```

---

### `CartSerializer`

```python
class CartSerializer(serializers.ModelSerializer):
    brand = serializers.SlugRelatedField(slug_field='slug', queryset=Brand.objects.all())
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    tier_discount = serializers.SerializerMethodField()
    discounted_total_price = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    current_tier = serializers.SerializerMethodField()
    can_checkout = serializers.SerializerMethodField()
```

**Purpose:** Serialize a user's cart, calculate discounts, and determine checkout eligibility.

**Main Logic Highlights:**

* `get_points()`: Gets the user’s **total points**.
* `get_brand_points()`: Fetch brand-specific points (or fallback).
* `get_applicable_tier()`: Chooses the **highest eligible tier** based on points.
* `get_tier_discount()`: Fetches the discount % from that tier.
* `get_current_tier()`: Returns tier details (used for showing progress or next level).
* `get_discounted_total_price()`: Applies the discount to cart total.
* `get_can_checkout()`: Returns True if user is eligible for checkout.

 **Context Awareness:** Uses `self.context['request'].user` to access user data.

---

### `TierDetailSerializer`

```python
class TierDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tier
        fields = ['points_required', 'discount_percent']
```

**Purpose:** Clean minimal serializer for tier data.

---

### `BrandTierSerializer`

```python
class BrandTierSerializer(serializers.Serializer):
    brand = serializers.CharField()
    tiers = TierDetailSerializer(many=True)
```

**Purpose:** Used for returning grouped brand tiers, like:

```json
{
  "brand": "nike",
  "tiers": [
    {"points_required": 100, "discount_percent": 5},
    ...
  ]
}
```

---

### `CheckoutResponseSerializer`

```python
class CheckoutResponseSerializer(serializers.Serializer):
    brand = serializers.CharField()
    discount = serializers.IntegerField()
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    coupon_code = serializers.CharField()
    website_url = serializers.URLField()
    message = serializers.CharField()
```

**Purpose:** Serializer used **only on checkout** success — provides user with:

* Final discounted price
* Applied coupon code
* Brand website to redirect to
* Message and discount info

---
Alright Basant, here’s your fully documented breakdown of all Django views — clean, dev-friendly, and perfect for your backend docs.
We'll go class-by-class and explain what each view does, when it’s used, and how it works under the hood.

---

## `views.py` Documentation

```python
from rest_framework import viewsets, status, filters as drf_filters, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from collections import defaultdict
from decimal import Decimal
from django.utils.crypto import get_random_string

from .models import (
    Product, Wishlist, Brand, Category,
    Cart, CartItem, UserBrandPoints, Tier, Coupon
)
from .serializers import (
    ProductSerializer, WishlistSerializer, BrandSerializer,
    CategorySerializer, CartItemSerializer, CartSerializer,
    BrandTierSerializer, TierDetailSerializer, CheckoutResponseSerializer
)
from .filters import ProductFilter
from rest_framework.permissions import IsAuthenticated
```

---

##  `ProductViewSet`

```python
class ProductViewSet(viewsets.ModelViewSet):
```

**Purpose:** Handles product listing, searching, filtering, and full CRUD (if allowed).
**Features:**

* `filterset_class = ProductFilter`: supports filtering like by brand, category, price range, etc.
* `search_fields`: allows keyword search by English name, Arabic name, and brand slug.
* Adds `is_wishlisted` to each product based on the current user (via context injection).

```python
def get_serializer_context(self):
    ...
```

Injects the wishlist product IDs into the serializer context to dynamically check `is_wishlisted`.

---

##  `WishlistAPIView`

```python
class WishlistAPIView(APIView):
```

**Purpose:** View to manage a user's wishlist.

**Methods:**

* `GET`: Return all products the user has wishlisted.
* `POST <id>`: Add product to wishlist by its ID.
* `DELETE <id>`: Remove product from wishlist by its ID.

Uses:

* `Wishlist.objects.get_or_create(user=request.user)` to ensure wishlist always exists.

---

## `BrandViewSet` / `CategoryViewSet`

```python
class BrandViewSet(viewsets.ModelViewSet):
class CategoryViewSet(viewsets.ModelViewSet):
```

**Purpose:** Full CRUD for brands and categories.
**Lookup by:** `slug`, not ID.
**Use case:** Easily build dropdowns, filters, or admin panels.

---

## `CartItemAPIView`

```python
class CartItemAPIView(APIView):
```

**Purpose:** Handle cart item CRUD operations:

* View all items
* Add/update items
* Delete items

**Enforces Single-Brand Rule:** Only products from one brand can exist in a cart.

**Methods:**

* `GET`: List all cart items.
* `POST`: Add product to cart or update quantity. Enforces brand rule.
* `PATCH <pk>`: Update quantity or fields of a cart item.
* `DELETE <pk>`: Remove item; resets cart brand if empty.

```python
def get_cart(self, user):
    ...
```

Helper to fetch or create a user’s cart.

---

## `CartSummaryAPIView`

```python
class CartSummaryAPIView(APIView):
```

**Purpose:** Return a full summary of the user's cart:

* Total price
* Tier-based discount
* Discounted total
* Eligibility to checkout
* Current tier and points

**Uses:** `CartSerializer` with full cart details including tier logic.

---

## `ListTiersAPIView`

```python
class ListTiersAPIView(APIView):
```

**Purpose:** List all tiers grouped by brand in one API response.
Useful for frontends that need to show all brands and their loyalty programs.

**Returns:**

```json
[
  {
    "brand": "curlit",
    "tiers": [
      { "points_required": 100, "discount_percent": 10 },
      ...
    ]
  }
]
```

---

## `BrandTierAPIView`

```python
class BrandTierAPIView(APIView):
```

**Purpose:** List tiers for a specific brand using its slug.
Use this when viewing a brand details page or store-specific benefits.

---

## `CheckoutAPIView`

```python
class CheckoutAPIView(APIView):
```

**Purpose:** Process the checkout using user points and apply discount via a coupon.

**Steps Handled:**

1. Get cart and validate it.
2. Find best applicable `Tier` based on `UserBrandPoints` or fallback to `user.total_points`.
3. Calculate discounted price.
4. Use matching coupon (same discount % and unused).
5. Deduct points:

    * From brand-specific if possible.
    * Fallback to user’s total points.
6. Mark coupon as used.
7. Clear the cart.

**Returns:** Serialized `CheckoutResponseSerializer` with:

* brand
* discount
* discounted price
* coupon code
* redirect website URL
* success message
---

##  Summary Cheat Sheet 

| Endpoint               | Method | Purpose                     |
| ---------------------- | ------ | --------------------------- |
| `/products/`           | GET    | List products               |
| `/wishlist/`           | GET    | Get wishlist                |
| `/wishlist/<id>/`      | POST   | Add product to wishlist     |
| `/wishlist/<id>/`      | DELETE | Remove from wishlist        |
| `/cart/items/`         | POST   | Add to cart                 |
| `/cart/items/<pk>/`    | PATCH  | Update item                 |
| `/cart/items/<pk>/`    | DELETE | Remove item                 |
| `/cart/`               | GET    | Full cart summary           |
| `/tiers/`              | GET    | All brands + their tiers    |
| `/tiers/<brand_slug>/` | GET    | Tiers for one brand         |
| `/checkout/`           | POST   | Apply discount + clear cart |

---
#### all rights back to Bassanthossamxx




