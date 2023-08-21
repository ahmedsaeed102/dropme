import django_filters
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from users_api.models import UserModel
from .models import Product, Cart, Entry


def product_get(*, pk: int) -> Product:
    return get_object_or_404(Product, pk=pk)


class ProductFilter(django_filters.FilterSet):
    price_points = django_filters.NumberFilter(lookup_expr="lte")

    class Meta:
        model = Product
        fields = ("price_points",)


class EntryService:
    def __init__(self, *, user: UserModel) -> None:
        self.user = user
        self.cart_init()

    def cart_init(self) -> Cart:
        cart = self.user.cart.filter(active=True).first()
        if cart:
            self.cart = cart
        else:
            self.cart = Cart.objects.create(user=self.user)

        return self.cart

    def entry_create(self, *, product: Product, quantity: int) -> Entry:
        return Entry.objects.create(cart=self.cart, product=product, quantity=quantity)

    @transaction.atomic
    def entry_add(self, *, data: dict) -> None:
        entry = self.entry_create(product=data["product"], quantity=data["quantity"])

        self.cart.count = self.cart.count + entry.quantity
        self.cart.total = self.cart.total + entry.product.price_points * entry.quantity

        self.cart.save()

    def entry_get(self, *, pk: int) -> Entry:
        return get_object_or_404(Entry, pk=pk)

    @transaction.atomic
    def entry_update(self, entry_id: int, qunatitiy: int) -> None:
        entry = self.entry_get(pk=entry_id)
        if entry.cart.user.id != self.user.id:
            raise PermissionDenied({"detail": "You are not allowed to edit this entry"})

        old_qunatity = entry.quantity

        entry.quantity = qunatitiy
        entry.save()

        if old_qunatity >= qunatitiy:
            self.cart.count = self.cart.count - (old_qunatity - qunatitiy)
            self.cart.total = (
                self.cart.total
                - (old_qunatity - qunatitiy) * entry.product.price_points
            )
        else:
            self.cart.count = self.cart.count + (qunatitiy - old_qunatity)
            self.cart.total = (
                self.cart.total
                + (qunatitiy - old_qunatity) * entry.product.price_points
            )

        self.cart.save()

    @transaction.atomic
    def entry_delete(self, *, entry_id: int) -> None:
        entry = self.entry_get(pk=entry_id)

        if entry.cart.user.id != self.user.id:
            raise PermissionDenied(
                {"detail": "You are not allowed to delete this entry"}
            )

        self.cart.count = self.cart.count - entry.quantity
        self.cart.total = self.cart.total - (
            entry.product.price_points * entry.quantity
        )

        entry.delete()
        self.cart.save()


def product_list(*, filters=None):
    filters = filters or {}

    qs = Product.objects.all()

    return ProductFilter(filters, qs).qs


# def product_coupon_get(*, request, product_id: int) -> str:
#     pass
