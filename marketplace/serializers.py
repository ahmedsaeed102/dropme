from rest_framework import serializers
from competition_api.models import Resource
from .models import Product, Cart, Entry, Category


class ProductSerializer(serializers.ModelSerializer):
    can_buy = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_can_buy(self, obj) -> bool:
        user = self.context["request"].user
        return user.total_points >= obj.price_points


class OutputEntrySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    entry_id = serializers.IntegerField(source="id")

    class Meta:
        model = Entry
        fields = ("entry_id", "product", "quantity")


class InputEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ("product", "quantity")


class EditEntrySerializer(serializers.Serializer):
    entry_id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class CartSerializer(serializers.ModelSerializer):
    items = OutputEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ("items", "count", "total")


class CheckoutSerializer(serializers.Serializer):
    products = serializers.ListSerializer(child=serializers.IntegerField())


class ProductFilterSerializer(serializers.Serializer):
    price_points = serializers.IntegerField(required=False)
    category__category_name = serializers.CharField(required=False)


class CategoryFilterSerializer(serializers.Serializer):
    category_name = serializers.CharField(required=False)


class CheckoutSerializer(serializers.Serializer):
    entry_ids = serializers.ListSerializer(child=serializers.IntegerField())


class CategorysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MarketplaceResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"


# class OfferSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SpecialOffer
#         fields = "__all__"
