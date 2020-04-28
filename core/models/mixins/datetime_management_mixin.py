from django.db import models
from django.utils.translation import ugettext_lazy as _


class DateTimeManagementMixin(models.Model):
    """
    Mixin to UUID as primary key
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        auto_now_add=True,
        null=False,
        blank=False,
        editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=_('updated at'),
        auto_now=True,
        null=False,
        blank=False,
        editable=False,
    )
