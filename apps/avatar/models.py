import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from stdimage import StdImageField
from stdimage.validators import MinSizeValidator, MaxSizeValidator

from apps.avatar.constants import AVATAR_TYPES, AVATAR_INTERNAL


def get_image_path(instance, filename):
    """ Resgata localização onde as imagens serão inseridas. """
    return os.path.join('avatars', str(instance.user.pk), filename)


class Avatar(models.Model):
    class Meta:
        verbose_name = _('Avatar')
        verbose_name_plural = _('Avatars')

    user = models.ForeignKey(
        to='user.User',
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='avatars',
        blank=False,
        null=False,
    )

    type = models.CharField(
        verbose_name=_('type'),
        max_length=8,
        choices=AVATAR_TYPES,
        default=AVATAR_INTERNAL,
        null=False,
        blank=False,
    )

    image = StdImageField(
        max_length=500,
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem principal',
        variations={'default': (640, 480), 'thumbnail': (200, 266, True)},
        validators=[MinSizeValidator(640, 480), MaxSizeValidator(1400, 1861)],
        help_text=_(
            'Avatars should be sent by mininum of 640px largura x 480px'
            ' altura.(png/jpg)'
        )
    )

    main = models.BooleanField(
        verbose_name=_('main'),
        null=False,
        blank=True,
        default=False,
    )
