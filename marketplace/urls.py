from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, WishlistAPIView, BrandViewSet, CategoryViewSet , CartItemListCreateAPIView , CartItemDetailAPIView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),  # /products/ and /products/<id>/
    path('wishlist/', WishlistAPIView.as_view()),  # GET wishlist
    path('wishlist/<int:id>/', WishlistAPIView.as_view()),  # POST and DELETE by product ID
    path('cart-items/', CartItemListCreateAPIView.as_view(), name='cart-items'),
    path('cart-items/<int:pk>/', CartItemDetailAPIView.as_view(), name='cart-item-detail'),
]
