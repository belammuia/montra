
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models import ImmutableModel
from core.cryptography.fields import EncryptedModelField


class Account(models.Model):

    class AccountType(models.TextChoices):
        PERSONAL = "PERSONAL", "Personal Wallet"
        MERCHANT = "MERCHANT", "Merchant Account"
        ESCROW = "ESCROW", "Escrow Account"
        REVENUE = "REVENUE", "Platform Fee Revenue"
        SETTLEMENT = "SETTLEMENT", "Bank Settlement Pool"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ledger_accounts"
    )

    name = models.CharField(
        max_length=150
    )

    account_type = models.CharField(
        max_length=30,
        choices=AccountType.choices,
        default=AccountType.PERSONAL
    )

    currency = models.CharField(
        max_length=3
    )


    account_reference = EncryptedModelField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["owner", "currency"],
                name="account_owner_currency_idx"
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="account_currency_valid"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.account_type})"


class Transaction(ImmutableModel):

    class TransactionType(models.TextChoices):
        TRANSFER = "TRANSFER", "Transfer"
        DEPOSIT = "DEPOSIT", "Deposit"
        WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
        PAYMENT = "PAYMENT", "Payment"
        REFUND = "REFUND", "Refund"
        FEE = "FEE", "Platform Fee"
        REVERSAL = "REVERSAL", "Reversal"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )

    description = models.TextField(
        blank=True
    )

    reverses = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reversed_by"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type}: {self.id}"


class Entry(ImmutableModel):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        related_name="entries"
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="entries"
    )

    # Signed integer in the currency's minor units.
    # Negative = debit, positive = credit.
    amount_minor = models.BigIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

        constraints = [
            models.CheckConstraint(
                condition=~Q(amount_minor=0),
                name="entry_amount_nonzero"
            ),
        ]

        indexes = [
            models.Index(
                fields=["account", "created_at"],
                name="entry_account_created_idx"
            ),
            models.Index(
                fields=["transaction"],
                name="entry_transaction_idx"
            ),
        ]

    def __str__(self):
        return (
            f"{self.transaction_id}: "
            f"{self.account_id} = {self.amount_minor}"
        )


class IdempotencyKey(models.Model):

    class ResponseStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="idempotency_keys"
    )

    key = models.CharField(
        max_length=255
    )

    request_hash = models.CharField(
        max_length=64
    )

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="idempotency_records"
    )

    response_status = models.CharField(
        max_length=12,
        choices=ResponseStatus.choices,
        default=ResponseStatus.PENDING
    )

    response_body = models.JSONField(
        default=dict
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "key"],
                name="unique_idempotency_per_user"
            ),
        ]

        indexes = [
            models.Index(
                fields=["user", "created_at"],
                name="idempotency_user_created_idx"
            ),
        ]

    def __str__(self):
        return f"{self.user_id}: {self.key}"
