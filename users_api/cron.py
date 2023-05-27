import kronos
from datetime import datetime
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)


@kronos.register("0 9 * * 5")
def flush_blacklisted_tokens():
    BlacklistedToken.objects.filter(token__expires_at__lt=datetime.now()).delete()
    OutstandingToken.objects.filter(expires_at__lt=datetime.now()).delete()
