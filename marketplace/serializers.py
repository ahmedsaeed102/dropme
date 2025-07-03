from rest_framework import serializers
from .models import Product, Wishlist, Brand, Category
from decimal import Decimal

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
            'description_en', 'description_ar', 'img_url',
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

































# class InputEntrySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Entry
#         fields = ("product", "quantity")
#
# class EditEntrySerializer(serializers.Serializer):
#     entry_id = serializers.IntegerField()
#     quantity = serializers.IntegerField()
#
# class OutputEntrySerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)
#     entry_id = serializers.IntegerField(source="id")
#
#     class Meta:
#         model = Entry
#         fields = ("entry_id", "product", "quantity")
#
# class CartSerializer(serializers.ModelSerializer):
#     items = OutputEntrySerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Cart
#         fields = ("items", "count", "total")
# class MarketplaceResourcesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Resource
#         fields = "__all__"
