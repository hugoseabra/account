from django.db import models
from django.utils.translation import ugettext_lazy as _

from .datetime_management_mixin import DateTimeManagementMixin


class AuditableMixin(DateTimeManagementMixin, models.Model):
    """
    Mixin to UUID as primary key
    """

    class Meta:
        abstract = True

    created_by = models.UUIDField(
        verbose_name=_('created by'),
        null=False,
        blank=False,
    )
    updated_by = models.UUIDField(
        verbose_name=_('updated by'),
        null=True,
        blank=True,
    )
