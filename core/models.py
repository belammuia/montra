
from django.core.exceptions import PermissionDenied
from django.db import models


class ImmutableQuerySet(models.QuerySet):

    def update(self, **kwargs):
        raise PermissionDenied(
            f"{self.model.__name__} records are immutable."
        )

    def delete(self):
        raise PermissionDenied(
            f"{self.model.__name__} records cannot be deleted."
        )

    def bulk_update(self, objs, fields, batch_size=None):
        raise PermissionDenied(
            f"{self.model.__name__} records are immutable."
        )


class ImmutableManager(models.Manager):

    def get_queryset(self):
        return ImmutableQuerySet(
            self.model,
            using=self._db
        )

    def bulk_create(self, objs, **kwargs):
        raise PermissionDenied(
            f"{self.model.__name__} records cannot be bulk-created."
            " Use the approved creation service."
        )


class ImmutableModel(models.Model):

    objects = ImmutableManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        if not self._state.adding:
            raise PermissionDenied(
                f"{self.__class__.__name__} records "
                "cannot be modified."
            )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied(
            f"{self.__class__.__name__} records "
            "cannot be deleted."
        )
