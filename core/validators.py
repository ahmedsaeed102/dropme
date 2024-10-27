import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    if not re.match(r"^1[0125]{1}", value):
        raise ValidationError(_("Phone number must start with 10 or 11 or 12 or 15"))

    if not re.match(r"^\d{10}$", value):
        raise ValidationError(_("Phone number must be 10 numbers"))
