from django.utils.translation import ugettext_lazy as _

AVATAR_GRAVATAR = 'gravatar'
AVATAR_INTERNAL = 'internal'
AVATAR_TYPES = (
    (AVATAR_GRAVATAR, _('Gravatar')),
    (AVATAR_INTERNAL, _('Internal')),
)

PIN_TYPE_VALIDATION = 'account_validation'
PIN_TYPE_PASS_RESET = 'password_reset'
PIN_TYPES = (
    (PIN_TYPE_VALIDATION, _('Validation')),
    (PIN_TYPE_PASS_RESET, _('Password reset')),
)
