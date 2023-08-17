import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    price_points = django_filters.NumberFilter(lookup_expr="lte")

    class Meta:
        model = Product
        fields = ("price_points",)


def product_list(*, filters=None):
    filters = filters or {}

    qs = Product.objects.all()

    return ProductFilter(filters, qs).qs


def product_code_get(*, request, product_id: int) -> None:
    pass


def entry_create():
    pass


def entry_get():
    pass


def entry_update(request, data: dict):
    pass


def entry_delete(*, request, entry_id: int) -> None:
    pass


def cart_add_entry(*, request, data: dict) -> None:
    pass
