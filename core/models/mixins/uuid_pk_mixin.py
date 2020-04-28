import uuid as uuid

from django.db import models


class UUIDPkMixin(models.Model):
    """
    Mixin to UUID as primary key
    """

    class Meta:
        abstract = True

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )
