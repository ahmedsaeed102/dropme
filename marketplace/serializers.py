from decimal import Decimal

from rest_framework import serializers

from .models import Product, Wishlist, Brand, Category , CartItem , Cart ,UserBrandPoints ,Tier


class ProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    brand = serializers.SlugRelatedField(
        slug_field='slug', queryset=Brand.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = [
            'id', 'name_en', 'name_ar', 'price', 'discount',
            'discounted_price', 'is_wishlisted',
            'description_en', 'description_ar', 'img_urls',
            'product_page_link', 'brand', 'category',
            'created_at', 'updated_at'
        ]

    def get_discounted_price(self, obj):
        if not obj.price:
            return Decimal("0.00")
        discount = Decimal(obj.discount) / Decimal(100)
        discounted_price = obj.price * (Decimal("1.00") - discount)
        return round(discounted_price, 2)

    def get_is_wishlisted(self, obj):
        wishlist_ids = {str(i) for i in self.context.get("wishlist_product_ids", set())}
        return str(obj.id) in wishlist_ids


class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name_en', read_only=True)
    price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'total_price']

    def get_price(self, obj):
        return obj.product.get_final_price()

    def get_total_price(self, obj):
        return obj.total_price()

class CartSerializer(serializers.ModelSerializer):
    brand = serializers.SlugRelatedField(
        slug_field='slug', queryset=Brand.objects.all())
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    tier_discount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    can_checkout = serializers.SerializerMethodField()  # 🟢 Checkout Button Logic

    class Meta:
        model = Cart
        fields = ['id', 'brand', 'total_price', 'tier_discount', 'final_price', 'points', 'can_checkout', 'cart_items']

    def get_total_price(self, obj):
        return obj.total_price()

    def get_user_points(self, user, brand):
        try:
            return UserBrandPoints.objects.get(user=user, brand=brand).points
        except UserBrandPoints.DoesNotExist:
            return 0

    def get_tier_discount(self, obj):
        user = self.context['request'].user
        points = self.get_user_points(user, obj.brand)
        tier = Tier.objects.filter(brand=obj.brand, points_required__lte=points).order_by('-points_required').first()
        return tier.discount_percent if tier else 0

    def get_points(self, obj):
        user = self.context['request'].user
        return self.get_user_points(user, obj.brand)

    def get_final_price(self, obj):
        total = obj.total_price()
        discount = self.get_tier_discount(obj)
        return total * (1 - discount / 100)

    def get_can_checkout(self, obj):
        user = self.context['request'].user
        points = self.get_user_points(user, obj.brand)
        has_valid_tier = Tier.objects.filter(brand=obj.brand, points_required__lte=points).exists()
        return has_valid_tier
