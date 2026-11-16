
import os

from cryptography.fernet import Fernet, MultiFernet
from django.core.exceptions import ImproperlyConfigured


def get_cipher() -> MultiFernet:
    raw_keys = os.environ.get("FIELD_ENCRYPTION_KEYS")

    if not raw_keys:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEYS is not configured."
        )

    key_values = [
        key.strip()
        for key in raw_keys.split(",")
        if key.strip()
    ]

    if not key_values:
        raise ImproperlyConfigured(
            "No valid encryption keys were provided."
        )

    try:
        keys = [Fernet(key.encode()) for key in key_values]
    except (ValueError, TypeError) as exc:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEYS contains an invalid Fernet key."
        ) from exc

    return MultiFernet(keys)
