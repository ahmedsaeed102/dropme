import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    price_points = django_filters.NumberFilter(lookup_expr="lte")
    category__category_name = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Product
        fields = ("price_points", "category__category_name")

    # @property
    # def qs(self):
    #     parent = super().qs
    #     author = getattr(self.request, 'user', None)

    #     return parent.filter(price_points=True) and parent.filter(author=author)
