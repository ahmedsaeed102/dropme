from rest_framework import serializers
from .models import SpecialOffer, Product, Cart, Entry


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOffer
        fields = "__all__"


class EntrySerializer(serializers.ModelField):
    product_data = ProductSerializer(read_only=True)

    class Meta:
        model = Entry
        fields = ("product", "product_data", "quantity")


class CartSerializer(serializers.ModelSerializer):
    items = EntrySerializer(source="items", many=True)

    class Meta:
        model = Cart
        fields = ("count", "total", "items")


class ProductFilterSerializer(serializers.Serializer):
    price_points = serializers.IntegerField()
