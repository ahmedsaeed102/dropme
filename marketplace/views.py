from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import date
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter

from competition_api.models import Resource
from .muqbis_products.populate_database import populate
from .models import Product, Category, SpecialOffer, Wishlist
from .serializers import ProductSerializer, ProductFilterSerializer, CartSerializer, InputEntrySerializer, EditEntrySerializer, MarketplaceResourcesSerializer, CategorysSerializer, CategoryFilterSerializer, SpecialOfferSerializer, WishlistSerializer
from .services import product_list, product_get, EntryService, checkout, category_list

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorysSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        filters_serializer = CategoryFilterSerializer(data=self.request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        categorys = category_list(filters=filters_serializer.validated_data)
        return categorys

    @extend_schema(parameters=[ OpenApiParameter(name="category_name", location=OpenApiParameter.QUERY, description="category name", required=False, type=str,),],)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProductsPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 100

class ProductsList(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = ProductsPagination

    def get_queryset(self):
        filters_serializer = ProductFilterSerializer(data=self.request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        products = product_list(filters=filters_serializer.validated_data)
        return products

    @extend_schema(parameters=[OpenApiParameter(name="price_points", location=OpenApiParameter.QUERY, description="product price points", required=False, type=int,),OpenApiParameter(name="category__category_name", location=OpenApiParameter.QUERY, description="product category", required=False, type=str,),],)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

class RelatedProducts(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        product = product_get(pk=self.kwargs["pk"])
        return (Product.objects.filter(price_points__lte=product.price_points).exclude(id=product.id).order_by("-price_points")[:5])

class WishlistView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        serializer = WishlistSerializer(wishlist, context={"request": request})
        return Response(serializer.data)

class AddToWishlistView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, product_id, *args, **kwargs):
        user = request.user
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "product not found"}, status=status.HTTP_404_NOT_FOUND)
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        wishlist.products.add(product)
        return Response({"status": "Products added to wishlist"}, status=status.HTTP_201_CREATED)

class RemoveFromWishlistView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, product_id, *args, **kwargs):
        user = request.user
        try:
            wishlist = Wishlist.objects.get(user=user)
        except Wishlist.DoesNotExist:
            return Response({"error": "Wishlist not found"}, status=status.HTTP_404_NOT_FOUND)
        wishlist.products.remove(product_id)
        return Response({"status": "Products removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)

class UserCart(APIView):
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_cart = request.user.cart.filter(active=True).first()
        return Response(self.serializer_class(user_cart, context={"request": request}).data)

class AddToCart(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InputEntrySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = EntryService(user=request.user)
        entry.entry_add(data=serializer.validated_data)
        return Response("Added to cart", status=status.HTTP_201_CREATED)

class EditCartEntry(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EditEntrySerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = EntryService(user=request.user)
        entry.entry_update(entry_id=serializer.data["entry_id"], qunatitiy=serializer.data["quantity"])
        return Response("Updated")

class RemoveFromCart(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, entry_id):
        entry = EntryService(user=request.user)
        entry.entry_delete(entry_id=entry_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

class Checkout(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        coupons = checkout(user=request.user)
        return Response(coupons)

class MarketplaceSlider(generics.ListAPIView):
    queryset = Resource.objects.filter(resource_type="marketplace")
    serializer_class = MarketplaceResourcesSerializer
    permission_classes = (permissions.IsAuthenticated,)

class SpecialOffersList(generics.ListAPIView):
    queryset = SpecialOffer.objects.filter(end_date__gte=date.today())
    serializer_class = SpecialOfferSerializer
    permission_classes = (permissions.IsAuthenticated,)

# class PopulateData(APIView):
#     """For populating database with muqbis products"""

#     permission_classes = (permissions.IsAdminUser,)

#     def get(self, request):
#         populate()
#         return Response("success")
