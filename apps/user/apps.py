from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UserConfig(AppConfig):
    name = 'apps.user'
    label = "user"
    verbose_name = _("Users")

    # noinspection PyUnresolvedReferences
    def ready(self):
        import apps.user.signals
