import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    price_points = django_filters.NumberFilter(lookup_expr="lte")

    class Meta:
        model = Product
        fields = ("price_points",)
