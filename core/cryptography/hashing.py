
import hashlib
import hmac
import os

from django.core.exceptions import ImproperlyConfigured


def make_blind(value: str) -> str:
    secret = os.environ.get("BLIND_SECRET_KEY")

    if not secret:
        raise ImproperlyConfigured(
            "BLIND_SECRET_KEY is not configured."
        )

    normalized = value.strip().casefold().encode("utf-8")

    return hmac.new(
        secret.encode("utf-8"),
        normalized,
        hashlib.sha256
    ).hexdigest()
