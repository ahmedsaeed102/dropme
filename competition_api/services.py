from django.shortcuts import get_object_or_404
from .models import Competition


def competition_get(*, pk: int) -> Competition:
    return get_object_or_404(Competition, pk=pk)
