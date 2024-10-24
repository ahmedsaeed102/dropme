from django.contrib import admin
from .models import Product, Cart, Entry, Category, SpecialOffer, UserOffer, Wishlist


admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Entry)
admin.site.register(Category)
admin.site.register(SpecialOffer)
admin.site.register(UserOffer)
admin.site.register(Wishlist)
