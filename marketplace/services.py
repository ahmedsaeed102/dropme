from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from users_api.models import UserModel
from .models import Product, Cart, Entry, Category
from .filters import ProductFilter, CategoryFilter


def product_get(*, pk: int) -> Product:
    return get_object_or_404(Product, pk=pk)


def product_list(*, filters: dict = None) -> QuerySet[Product]:
    filters = filters or {}
    qs = Product.objects.all()

    return ProductFilter(filters, qs).qs


def category_list(*, filters: dict = None) -> QuerySet[Category]:
    filters = filters or {}
    qs = Category.objects.all()

    return CategoryFilter(filters, qs).qs


def cart_get(*, user: UserModel) -> Cart | None:
    return user.cart.filter(active=True).first()


class EntryService:
    def __init__(self, *, user: UserModel) -> None:
        self.user = user
        self.cart_init()

    def cart_init(self) -> Cart:
        cart = cart_get(user=self.user)
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
        self.cart.total = self.cart.total + (
            entry.product.price_points * entry.quantity
        )

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
            diffrence = old_qunatity - qunatitiy

            self.cart.count = self.cart.count - diffrence
            self.cart.total = self.cart.total - (diffrence * entry.product.price_points)
        else:
            diffrence = qunatitiy - old_qunatity

            self.cart.count = self.cart.count + diffrence
            self.cart.total = self.cart.total + (diffrence * entry.product.price_points)

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


@transaction.atomic
def checkout(*, user: UserModel) -> dict:
    cart = cart_get(user=user)
    if not cart:
        raise PermissionDenied({"detail": "You have no items in cart"})

    if cart.total > user.total_points:
        raise PermissionDenied({"detail": "You don't have enough points"})

    coupons = {}

    for item in cart.items.all():
        coupons.update({f"{item.product.product_name_en}": item.product.coupon})

    user.total_points = user.total_points - cart.total
    user.save()

    cart.active = False
    cart.save()

    return coupons
