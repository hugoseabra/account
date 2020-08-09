import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from stdimage import StdImageField
from stdimage.validators import MinSizeValidator, MaxSizeValidator

from core.models.mixins import UUIDPkMixin, DateTimeManagementMixin


def get_image_path(instance, filename):
    """ Resgata localização onde as imagens serão inseridas. """
    ext = filename.split('.')[-1]
    filename = f'{instance.pk}.{ext}'
    return os.path.join('avatars', str(instance.user.pk), filename)


class Avatar(UUIDPkMixin, DateTimeManagementMixin):
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

    image = StdImageField(
        max_length=500,
        upload_to=get_image_path,
        blank=False,
        null=False,
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
        default=True,
    )

    def __str__(self):
        return self.image.name

    def __repr__(self):
        return f'<Avatar username={self.user} main={self.main}/>'
