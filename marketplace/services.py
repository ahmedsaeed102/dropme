from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from users_api.models import UserModel
from .models import Product, Cart, Entry, Category, SpecialOffer, UserOffer
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
            raise PermissionDenied(
                {"detail": _("You are not allowed to edit this entry")}
            )

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
                {"detail": _("You are not allowed to delete this entry")}
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
        raise PermissionDenied({"detail": _("You have no items in cart")})

    if cart.total > user.total_points:
        raise PermissionDenied({"detail": _("You don't have enough points")})

    coupons = {}

    for item in cart.items.all():
        coupons.update(
            {
                f"{item.product.product_name}": item.product.coupon,
                "link": item.product.product_page_link,
            }
        )

    user.total_points = user.total_points - cart.total
    user.save()

    cart.active = False
    cart.save()

    return coupons


def special_offer_apply(*, user: UserModel, points: int) -> int:
    offer = SpecialOffer.objects.filter(is_finished=False).first()

    if offer:
        user_offer = UserOffer.objects.filter(user=user, offer=offer).first()

        if user_offer:
            if user_offer.can_be_used:
                if points >= user_offer.remaining_amount:
                    user_offer.remaining_amount = 0
                    user_offer.can_be_used = False
                    user_offer.save()
                    return offer.reward_points
                else:
                    user_offer.remaining_amount = user_offer.remaining_amount - points
                    user_offer.save()
        else:
            if points >= offer.required_points:
                return offer.reward_points
            else:
                remaining = offer.required_points - points
                UserOffer.objects.create(
                    user=user, offer=offer, remaining_amount=remaining
                )

    return 0
