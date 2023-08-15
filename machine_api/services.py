import django_filters
from .models import Machine


class MachineFilter(django_filters.FilterSet):
    identification_name = django_filters.CharFilter(lookup_expr="icontains")
    city = django_filters.CharFilter(lookup_expr="icontains")
    place = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Machine
        fields = ("identification_name", "city", "place")


def machine_list(*, filters=None):
    filters = filters or {}

    qs = Machine.objects.all()

    return MachineFilter(filters, qs).qs
