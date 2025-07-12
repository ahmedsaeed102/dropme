import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
   FilterSet for filtering Product objects by brand and category slugs.

    Fields:
    brand (CharFilter): Filter by brand slug (case-insensitive).
    category (CharFilter): Filter by category slug (case-insensitive).
    """
    brand = django_filters.CharFilter(field_name='brand__slug', lookup_expr='iexact')
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')

    class Meta:
        model = Product
        fields = ['brand', 'category']
