import random
import string
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.user import constants
from core.models.mixins import (
    EntityMixin,
    DateTimeManagementMixin,
    UUIDPkMixin,
)


class Pin(UUIDPkMixin, DateTimeManagementMixin, EntityMixin):
    class Meta:
        verbose_name = _('Pin')
        verbose_name_plural = _('Pins')

    user = models.OneToOneField(
        to='user.User',
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='pin',
        blank=False,
        null=False,
    )

    pin_type = models.CharField(
        verbose_name=_('Pin Type'),
        max_length=18,
        choices=constants.PIN_TYPES,
        editable=False,
        null=False,
        blank=False,
    )

    pin = models.CharField(
        verbose_name=_('Pin'),
        max_length=8,
        null=False,
        blank=False,
    )

    exp_date = models.DateTimeField(
        verbose_name=_('expiration date'),
        editable=False,
        null=False,
        blank=False,
    )

    @property
    def is_expired(self):
        now = timezone.now()
        return self.exp_date < now

    @property
    def is_validation_pin(self):
        return self.pin_type == constants.PIN_TYPE_VALIDATION

    @property
    def is_password_reset_pin(self):
        return self.pin_type == constants.PIN_TYPE_PASS_RESET

    def save(self, *args, **kwargs):
        if self.is_new is True:
            self.set_pin()
            self.renew_expiration_date()

        super().save(*args, **kwargs)

    def set_pin(self, length=8, force_reset=False):
        if force_reset is False and self.pin:
            return

        self.pin = ''.join(
            random.choice(string.digits) for x in range(length)
        )

    def renew_expiration_date(self, save=False):
        self.exp_date = timezone.localtime() + timedelta(hours=24)
        if save:
            self.save()

    def renew(self, save=False):
        self.set_pin(force_reset=True)
        self.renew_expiration_date()
        if save:
            self.save()

    def __str__(self):
        return self.pin

    def __repr__(self):
        return f'<Pin username={self.user} ' \
               f'pin={self.pin} ' \
               f'exp_date={self.exp_date.timestamp()}/>'
