from rest_framework import viewsets, status, filters as drf_filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Wishlist ,Brand,Category
from .serializers import ProductSerializer, WishlistSerializer , BrandSerializer, CategorySerializer
from .filters import ProductFilter
from rest_framework.permissions import IsAuthenticated


#  Product ViewSet

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('brand', 'category').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name_en','name_ar','brand__name']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        print("User:", user)  # ✅ TEMPORARY for debugging

        if user.is_authenticated:
            wishlist = Wishlist.objects.filter(user=user).first()
            context["wishlist_product_ids"] = (
                set(wishlist.products.values_list("id", flat=True)) if wishlist else set()
            )
        else:
            context["wishlist_product_ids"] = set()

        return context



class WishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Important fix

    def get(self, request):
        """Return all products in the user's wishlist"""
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(wishlist, context={"request": request})
        return Response(serializer.data)

    def post(self, request, id):
        """Add product (by ID from URL) to the wishlist"""
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.add(product)
        return Response({"detail": "Product added to wishlist."}, status=status.HTTP_200_OK)

    def delete(self, request, id):
        """Remove product (by ID from URL) from the wishlist"""
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.remove(product)
        return Response({"detail": "Product removed from wishlist."}, status=status.HTTP_200_OK)
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


















# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import cache_page
# from django.db.models import Sum
# from datetime import date
# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.pagination import LimitOffsetPagination
# from drf_spectacular.utils import extend_schema, OpenApiParameter
#
# from competition_api.models import Resource
# from .muqbis_products.populate_database import populate
# from .models import Product, Category, SpecialOffer, Wishlist
# from machine_api.models import RecycleLog
# from .serializers import ProductSerializer, ProductFilterSerializer, CartSerializer, InputEntrySerializer, EditEntrySerializer, MarketplaceResourcesSerializer, CategorysSerializer, CategoryFilterSerializer, SpecialOfferSerializer, WishlistSerializer
# from machine_api.serializers import RecycleLogSerializer
# from machine_api.utlis import get_total_recycled_items
# #
# # class ProductsPagination(LimitOffsetPagination):
# #     default_limit = 5
# #     max_limit = 100
# #
#
#
# #will update it to slug too
# class WishlistView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get(self, request, *args, **kwargs):
#         user = request.user
#         wishlist, created = Wishlist.objects.get_or_create(user=user)
#         serializer = WishlistSerializer(wishlist, context={"request": request})
#         return Response(serializer.data)
#
# class AddToWishlistView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def post(self, request, product_id, *args, **kwargs):
#         user = request.user
#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "product not found"}, status=status.HTTP_404_NOT_FOUND)
#         wishlist, created = Wishlist.objects.get_or_create(user=user)
#         wishlist.products.add(product)
#         return Response({"status": "Products added to wishlist"}, status=status.HTTP_201_CREATED)
#
# class RemoveFromWishlistView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def delete(self, request, product_id, *args, **kwargs):
#         user = request.user
#         try:
#             wishlist = Wishlist.objects.get(user=user)
#         except Wishlist.DoesNotExist:
#             return Response({"error": "Wishlist not found"}, status=status.HTTP_404_NOT_FOUND)
#         wishlist.products.remove(product_id)
#         return Response({"status": "Products removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)
#
#
# # class UserCart(APIView):
# #     serializer_class = CartSerializer
# #     permission_classes = (permissions.IsAuthenticated,)
# #
# #     def get(self, request):
# #         user_cart = request.user.cart.filter(active=True).first()
# #         return Response(self.serializer_class(user_cart, context={"request": request}).data)
# #
# # class AddToCart(APIView):
# #     permission_classes = (permissions.IsAuthenticated,)
# #     serializer_class = InputEntrySerializer
# #
# #     def post(self, request):
# #         serializer = self.serializer_class(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         entry = EntryService(user=request.user)
# #         entry.entry_add(data=serializer.validated_data)
# #         return Response("Added to cart", status=status.HTTP_201_CREATED)
# #
# # class EditCartEntry(APIView):
# #     permission_classes = (permissions.IsAuthenticated,)
# #     serializer_class = EditEntrySerializer
# #
# #     def patch(self, request):
# #         serializer = self.serializer_class(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         entry = EntryService(user=request.user)
# #         entry.entry_update(entry_id=serializer.data["entry_id"], qunatitiy=serializer.data["quantity"])
# #         return Response("Updated")
# #
# # class RemoveFromCart(APIView):
# #     permission_classes = (permissions.IsAuthenticated,)
# #
# #     def delete(self, request, entry_id):
# #         entry = EntryService(user=request.user)
# #         entry.entry_delete(entry_id=entry_id)
# #         return Response(status=status.HTTP_204_NO_CONTENT)
# #
# # class Checkout(APIView):
# #     permission_classes = (permissions.IsAuthenticated,)
# #
# #     def get(self, request):
# #         coupons = checkout(user=request.user)
# #         return Response(coupons)
# #
# # class MarketplaceSlider(generics.ListAPIView):
# #     queryset = Resource.objects.filter(resource_type="marketplace")
# #     serializer_class = MarketplaceResourcesSerializer
# #     permission_classes = (permissions.IsAuthenticated,)
# #
# #
# # # class WalletPageView(generics.GenericAPIView):
# # #     permission_classes = (permissions.IsAuthenticated,)
# # #
# # #     def get(self, request):
# # #         user = request.user
# # #         user_points = user.total_points
# # #         logs = RecycleLog.objects.filter(user=request.user.id, is_complete=True).order_by('created_at')
# # #         log_serializer = RecycleLogSerializer(logs, many=True, context={"request": request}).data
# # #         return Response(
# # #             {
# # #                 "user_points": user_points,
# # #                 "recycled_items": get_total_recycled_items(user.id),
# # #                 "bottles_number": logs.aggregate(Sum("bottles"))["bottles__sum"] if logs else 0,
# # #                 "cans_number": logs.aggregate(Sum("cans"))["cans__sum"] if logs else 0,
# # #                 "other_number": 0,
# # #                 "recycle_logs": log_serializer
# # #             }, status=200
# # #         )
# #
# # class PopulateData(APIView):
# #     """For populating database with muqbis products"""
# #
# #     permission_classes = (permissions.IsAdminUser,)
# #
# #     def get(self, request):
# #         populate()
# #         return Response("success")
