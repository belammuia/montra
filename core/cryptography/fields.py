
from cryptography.fernet import InvalidToken
from django.db import models
from django.core.exceptions import ImproperlyConfigured

from .ciphers import get_cipher


class EncryptedModelField(models.TextField):

    description = "Text field encrypted using Fernet"

    def get_prep_value(self, value):
        if value is None:
            return None

        value = super().get_prep_value(value)

        return get_cipher().encrypt(
            value.encode("utf-8")
        ).decode("utf-8")

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None

        try:
            return get_cipher().decrypt(
                value.encode("utf-8")
            ).decode("utf-8")

        except InvalidToken as exc:
            raise ImproperlyConfigured(
                "Unable to decrypt database value. "
                "Check FIELD_ENCRYPTION_KEYS."
            ) from exc
