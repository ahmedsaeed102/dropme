from django.urls import path
from . import views

urlpatterns = [
    # category
    path("marketplace/categories/", views.CategoryList.as_view(), name="categories"),
    # products
    path("marketplace/products/", views.ProductsList.as_view(), name="products"),
    path("marketplace/products/<int:pk>/", views.ProductDetail.as_view(), name="product_detail",),
    path("marketplace/products/<int:pk>/related_products/", views.RelatedProducts.as_view(), name="related_products",),
    # WishList
    path('marketplace/products/wishlist/', views.WishlistView.as_view(), name='wishlist-list'),
    path('marketplace/products/<int:product_id>/wishlist/add/', views.AddToWishlistView.as_view(), name='wishlist-add'),
    path('marketplace/products/<int:product_id>/wishlist/remove/', views.RemoveFromWishlistView.as_view(), name='wishlist-remove'),
    # cart
    path("marketplace/cart/", views.UserCart.as_view(), name="cart"),
    path("marketplace/cart/add", views.AddToCart.as_view(), name="cart_add"),
    path("marketplace/cart/edit", views.EditCartEntry.as_view(), name="cart_edit"),
    path("marketplace/cart/<int:entry_id>/delete", views.RemoveFromCart.as_view(), name="cart_delete",),
    # checkout
    path("marketplace/cart/checkout/", views.Checkout.as_view(), name="checkout"),
    # slider
    path("marketplace/slider/", views.MarketplaceSlider.as_view(), name="marketplace_slider",),
    # special offer
    path("marketplace/special_offer/", views.SpecialOffersList.as_view(), name="special_offer_list",),
    # populate data
    # path("marketplace/populate/", views.PopulateData.as_view())
]
