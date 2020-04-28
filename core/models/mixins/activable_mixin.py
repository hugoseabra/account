from django.db import models
from django.utils.translation import ugettext_lazy as _


class ActivableMixin(models.Model):
    """
    Mixin for activable
    """

    class Meta:
        abstract = True

    active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
        null=False,
        blank=False,
    )
