from django.utils.translation import ugettext_lazy as _

AVATAR_GRAVATAR = 'gravatar'
AVATAR_INTERNAL = 'internal'
AVATAR_TYPES = (
    (AVATAR_GRAVATAR, _('Gravatar')),
    (AVATAR_INTERNAL, _('Internal')),
)
