from rest_framework import viewsets, status, filters as drf_filters , permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Wishlist ,Brand,Category,Cart, CartItem , UserBrandPoints , Tier
from .serializers import ProductSerializer, WishlistSerializer , BrandSerializer, CategorySerializer , CartItemSerializer , CartSerializer , BrandTierSerializer , TierDetailSerializer
from .filters import ProductFilter
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from collections import defaultdict

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


#CartView to Handle cart item retrieval, addition, update, and deletion for users
class CartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]
    # Retrieve or create a cart for the user
    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get(self, request):
        # Get all items in the user's cart
        cart = self.get_cart(request.user)
        items = cart.cart_items.all()
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Add a product to the cart or update its quantity
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data.get('quantity', 1)
            cart = self.get_cart(request.user)
            # Ensure only one brand per cart
            if cart.brand and cart.brand != product.brand:
                return Response({"error": "Only one brand allowed per cart."}, status=status.HTTP_400_BAD_REQUEST)
            # Set cart brand if not already set
            if not cart.brand:
                cart.brand = product.brand
                cart.save()

            item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            # Get or create the cart item
            if not created:
                item.quantity += quantity  # If item exists, increment quantity
                item.save()
            else:
                item.quantity = quantity # If new item, set quantity
                item.save()

            return Response(CartItemSerializer(item).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        # Update a cart item's quantity or details
        cart = self.get_cart(request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        serializer = CartItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Remove a cart item; reset cart brand if cart is empty
        cart = self.get_cart(request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()

        if not cart.cart_items.exists():
            cart.brand = None
            cart.save()
            return Response({"detail": "Item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


#view for get all cart summary
class CartSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    #get :
    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            #if no cart applied before
        except Cart.DoesNotExist:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_404_NOT_FOUND)
        #if no items in cart
        if not cart.cart_items.exists():
            return Response({"detail": "No items in cart."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartSerializer(cart, context={"request": request})
        #return data
        return Response(serializer.data , status=status.HTTP_200_OK)

#view to list every brand and dic of tiers
class GroupedTiersAPIView(APIView):
    def get(self, request):
        tiers = Tier.objects.select_related('brand').order_by('brand__name', 'points_required')
        grouped = defaultdict(list)

        for tier in tiers:
            grouped[tier.brand.slug].append(tier)

        result = []
        for brand_slug, brand_tiers in grouped.items():
            result.append({
                "brand": brand_slug,
                "tiers": TierDetailSerializer(brand_tiers, many=True).data
            })

        return Response(result)

#view for specific brand tier
class BrandTierDetailAPIView(APIView):
    def get(self, request, brand_slug):
        try:
            brand = Brand.objects.get(slug=brand_slug)
        except Brand.DoesNotExist:
            return Response({"detail": "Brand not found."}, status=status.HTTP_404_NOT_FOUND)

        tiers = Tier.objects.filter(brand=brand).order_by('points_required')
        data = {
            "brand": brand.slug,
            "tiers": TierDetailSerializer(tiers, many=True).data
        }

        return Response(data, status=200)


