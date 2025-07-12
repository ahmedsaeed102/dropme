from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, WishlistAPIView, BrandViewSet, CategoryViewSet , CartSummaryAPIView , CartItemAPIView , BrandTierAPIView , ListTiersAPIView , CheckoutAPIView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),  # /products/ and /products/<id>/
    path('wishlist/', WishlistAPIView.as_view()),  # GET wishlist
    path('wishlist/<int:id>/', WishlistAPIView.as_view()),  # POST and DELETE by product ID
    # Cart Items CRUD (GET, POST, PATCH, DELETE)
    path('cart/items/', CartItemAPIView.as_view(), name='cart-items'),          # GET all or POST add
    path('cart/items/<int:pk>/', CartItemAPIView.as_view(), name='cart-item'),  # PATCH/DELETE single item

    # Cart summary (total + discount + final + points + can do checkout or no)
    path('cart/', CartSummaryAPIView.as_view(), name='cart-summary'),
    # get specific brand tiers & discount percentage
    path('tiers/<slug:brand_slug>/', BrandTierAPIView.as_view(), name='brand-tier-detail'),
    # get all brands tiers
    path('tiers/', ListTiersAPIView.as_view(), name='tier-list'),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),

]
