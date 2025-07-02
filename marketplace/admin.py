from django.contrib import admin
from .models import Product, Category,Wishlist,Brand


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Wishlist)
