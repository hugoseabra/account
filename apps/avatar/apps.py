from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class AvatarConfig(AppConfig):
    name = 'apps.avatar'
    label = 'avatar'
    verbose_name = _('Avatar')
