from rest_framework import viewsets, status, filters as drf_filters , permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Wishlist ,Brand,Category,Cart, CartItem , UserBrandPoints
from .serializers import ProductSerializer, WishlistSerializer , BrandSerializer, CategorySerializer , CartItemSerializer , CartSerializer
from .filters import ProductFilter
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

#  Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('brand', 'category').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name_en','name_ar','brand__slug']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        if user.is_authenticated:
            wishlist = Wishlist.objects.filter(user=user).first()
            context["wishlist_product_ids"] = (
                set(wishlist.products.values_list("id", flat=True)) if wishlist else set()
            )
        else:
            context["wishlist_product_ids"] = set()

        return context

class WishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all products in the user's wishlist"""
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(wishlist, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        return Response({"detail": "Product removed from wishlist."}, status=status.HTTP_204_NO_CONTENT)

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class CartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get(self, request):
        cart = self.get_cart(request.user)
        items = cart.cart_items.all()
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data.get('quantity', 1)
            cart = self.get_cart(request.user)

            if cart.brand and cart.brand != product.brand:
                return Response({"error": "Only one brand allowed per cart."}, status=status.HTTP_400_BAD_REQUEST)

            if not cart.brand:
                cart.brand = product.brand
                cart.save()

            item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                item.quantity += quantity
                item.save()
            else:
                item.quantity = quantity
                item.save()

            return Response(CartItemSerializer(item).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        cart = self.get_cart(request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        serializer = CartItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cart = self.get_cart(request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()

        if not cart.cart_items.exists():
            cart.brand = None
            cart.save()
            return Response({"detail": "Item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class CartSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart is empty."}, status=404)

        if not cart.cart_items.exists():
            return Response({"detail": "No items in cart."}, status=400)

        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data)





