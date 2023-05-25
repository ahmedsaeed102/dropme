import re
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    if not re.match(r"^01[0125]{1}", value):
        raise ValidationError("Phone number must start with 010 or 011 or 012 or 015")

    if not re.match(r"^\d{11}$", value):
        raise ValidationError("Phone number must be 11 numbers")
