import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    if not re.match(r"^1[0125]{1}", value):
        raise ValidationError(_("Phone number must start with 010 or 011 or 012 or 015"))

    if not re.match(r"^\d{11}$", value):
        raise ValidationError(_("Phone number must be 11 numbers"))
