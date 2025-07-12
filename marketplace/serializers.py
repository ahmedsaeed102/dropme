from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from .models import Product, Wishlist, Brand, Category, CartItem, Cart, UserBrandPoints, Tier


class ProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()
    #check if the product is in the user's wishlist
    is_wishlisted = serializers.SerializerMethodField()
    brand = serializers.SlugRelatedField(
        slug_field='slug', queryset=Brand.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())

    class Meta:
        model = Product
        ordering = ['-created_at']
        fields = [
            'id', 'name_en', 'name_ar', 'price', 'discount',
            'discounted_price', 'is_wishlisted',
            'description_en', 'description_ar', 'img_urls',
            'product_page_link', 'brand', 'category',
            'created_at', 'updated_at'
        ]

    def get_discounted_price(self, obj):
        """
        Returns the price after applying the discount.
        """
        if not obj.price:
            return Decimal("0.00")
        discount = Decimal(obj.discount) / Decimal(100)
        discounted_price = obj.price * (Decimal("1.00") - discount)
        return round(discounted_price, 2)

    def get_is_wishlisted(self, obj):
        """
        Returns True if the product is in the user's wishlist.
        """
        wishlist_ids = {str(i) for i in self.context.get("wishlist_product_ids", set())}
        return str(obj.id) in wishlist_ids


class WishlistSerializer(serializers.ModelSerializer):
    """
     Serializer for the Wishlist model, including related products.
    """
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products']


class BrandSerializer(serializers.ModelSerializer):
    """
   Serializer for the Brand model, exposing id, name, and slug fields.
   The slug field is read-only.
   """
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model, exposing id, name, and slug fields.
    The slug field is read-only.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the CartItem model, providing product details,
    price per item, and total price for the cart item.
    """
    product_name = serializers.CharField(source='product.name_en', read_only=True)
    price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'total_price']

    def get_price(self, obj):
        """
        Returns the final price of the product for this cart item.
        """
        return obj.product.get_final_price()

    def get_total_price(self, obj):
        """
        Returns the total price for this cart item (price * quantity).
        """
        return obj.total_price()


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model, including brand, cart items, and pricing/tier details.
    """
    brand = serializers.SlugRelatedField(
        slug_field='slug', queryset=Brand.objects.all()
    )
    cart_items = CartItemSerializer(many=True, read_only=True)

    total_price = serializers.SerializerMethodField()
    tier_discount = serializers.SerializerMethodField()
    discounted_total_price = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()         # User total points
    current_tier = serializers.SerializerMethodField()   # Tier info
    can_checkout = serializers.SerializerMethodField()   # Checkout button logic

    class Meta:
        model = Cart
        fields = [
            'id', 'brand', 'total_price',
            'tier_discount', 'discounted_total_price',
            'points', 'current_tier',
            'can_checkout', 'cart_items'
        ]

    def get_total_price(self, obj):
        """
        Returns the total price of all items in the cart before discounts.
        """
        total = obj.total_price()
        return round(Decimal(total), 2)

    def get_points(self, obj):
        """
        Returns the user's total points.
        """
        return self.context['request'].user.total_points

    def get_brand_points(self, obj):
        """
        Returns the user's points for the specific brand, or total points if not found.
        """
        user = self.context['request'].user
        try:
            return UserBrandPoints.objects.get(user=user, brand=obj.brand).points
        except UserBrandPoints.DoesNotExist:
            # fallback to total points (if no brand-specific record)
            return user.total_points

    def get_applicable_tier(self, brand, points):
        """
        Returns the highest applicable tier for the given brand and points.
        """
        return Tier.objects.filter(
            brand=brand, points_required__lte=points
        ).order_by('-points_required').first()

    def get_tier_discount(self, obj):
        """
        Returns the discount percentage for the user's current tier.
        """
        tier = self.get_applicable_tier(obj.brand, self.get_brand_points(obj))
        return tier.discount_percent if tier else 0

    def get_current_tier(self, obj):
        """
        Returns a dict with the current tier's discount and required points, or None.
        """
        tier = self.get_applicable_tier(obj.brand, self.get_brand_points(obj))
        if tier:
            return {
                "discount": tier.discount_percent,
                "required_points": tier.points_required
            }
        return None

    def get_discounted_total_price(self, obj):
        """
        Returns the total price after applying the tier discount.
        """
        total = Decimal(obj.total_price())
        discount = self.get_tier_discount(obj)
        discounted = total * (Decimal("1") - Decimal(discount) / 100)
        return discounted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def get_can_checkout(self, obj):
        """
        Returns True if the user can checkout (i.e., a discount is available).
        """
        return self.get_tier_discount(obj) > 0


class TierDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tier model, exposing points required and discount percent fields.
    """
    class Meta:
        model = Tier
        fields = ['points_required', 'discount_percent']


class BrandTierSerializer(serializers.Serializer):
    """
    Serializer for representing a brand and its associated tiers.
    """
    brand = serializers.CharField()
    tiers = TierDetailSerializer(many=True)


class CheckoutResponseSerializer(serializers.Serializer):
    """
    Serializer for the checkout response, including brand, discount, discounted price,
    coupon code, website URL, and a message.
    """
    brand = serializers.CharField()
    discount = serializers.IntegerField()
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    coupon_code = serializers.CharField()
    website_url = serializers.URLField()
    message = serializers.CharField()

