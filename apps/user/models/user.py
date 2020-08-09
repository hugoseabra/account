from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.user import constants
from core.models.mixins import (
    UUIDPkMixin,
    DateTimeManagementMixin,
    EntityMixin,
)
from core.validators import cpf_validator
from .pin import Pin
from ..exceptions import PinCreationImpossibility


class UserManager(BaseUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        """ Make all emails lower case """
        email = email or ""
        return email.lower()

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True,
                  backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )

        backend = auth.load_backend(backend)

        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )

        return self.none()


class User(UUIDPkMixin,
           DateTimeManagementMixin,
           EntityMixin,
           AbstractBaseUser,
           PermissionsMixin):
    """
    Conta de usuário da Congressy
    """

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    EMAIL_FIELD = "email"
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    first_name = models.CharField(
        verbose_name=_("first name"),
        max_length=30,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name=_("last name"),
        max_length=150,
        blank=True,
        null=True,
    )
    is_staff = models.BooleanField(
        verbose_name=_("staff status"),
        default=False,
        null=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        verbose_name=_("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_validated = models.BooleanField(
        verbose_name=_("validated"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as validated. "
            "This is taken actively by the user itself though a proof that "
            "his has access to the provided e-mail."
        ),
    )
    password_deactivated = models.BooleanField(
        verbose_name=_("password deactivated"),
        default=False,
        help_text=_(
            "Designates whether this user must redefine his password. "
            "When, we assume the current password is not valid."
        ),
    )
    cpf = models.CharField(
        verbose_name='CPF',
        max_length=11,
        blank=True,
        null=True,
        unique=True,
        validators=[cpf_validator]
    )

    avatar_type = models.CharField(
        verbose_name=_('type'),
        max_length=8,
        choices=constants.AVATAR_TYPES,
        default=constants.AVATAR_INTERNAL,
        null=False,
        blank=False,
    )

    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now,
        null=True,
    )

    @property
    def cpf_formatted(self):
        if not self.cpf:
            return None

        return '{0}.{1}.{2}-{3}'.format(
            self.cpf[:3],
            self.cpf[3:6],
            self.cpf[6:9],
            self.cpf[9:11]
        )

    @property
    def avatar(self):
        return self.avatars.filter(main=True).first()

    @property
    def is_gravatar_avatar(self):
        return self.avatar_type == constants.AVATAR_GRAVATAR

    @property
    def is_internal_avatar(self):
        return self.avatar_type == constants.AVATAR_INTERNAL

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    def deactivate_password(self):
        self.password_deactivated = True
        self.password = None
        self.save()

    def get_validation_pin(self):
        pin = None
        try:
            if self.pin.is_validation_pin is True:
                pin = self.pin

        except Pin.DoesNotExist:
            pass

        return pin

    def get_password_reset_pin(self):
        pin = None
        try:
            if self.pin.is_password_reset_pin is True:
                pin = self.pin

        except Pin.DoesNotExist:
            pass

        return pin

    def create_or_renew_validation_pin(self):
        if self.is_new is True:
            raise PinCreationImpossibility(_(
                'You cannot create PIN before saving the user.'
            ))

        if self.is_validated is True:
            raise PinCreationImpossibility(_(
                'You cannot create PIN to validate an account when the user'
                ' is already validated.'
            ))

        pin = self.get_validation_pin()

        if pin:
            if pin.is_expired is True:
                pin.renew()
        else:
            pin = Pin.objects.create(
                user=self,
                pin_type=constants.PIN_TYPE_VALIDATION
            )

        return pin

    def create_or_renew_password_pin(self):
        if self.is_new is True:
            raise PinCreationImpossibility(_(
                'You cannot create PIN before saving the user.'
            ))

        if self.is_validated is False:
            raise PinCreationImpossibility(_(
                'You cannot create PIN to reset password when the user'
                ' is validated yet.'
            ))

        pin = self.get_password_reset_pin()
        if pin:
            if pin.is_expired is True:
                pin.renew()
        else:
            pin = Pin.objects.create(
                user=self,
                pin_type=constants.PIN_TYPE_PASS_RESET
            )

        return pin

    def validate(self):
        self.is_validated = True
        self.save()

        pin = self.get_validation_pin()
        if pin:
            pin.delete()

    def __str__(self):
        return self.email

    def __repr__(self):
        return f'<User username={self.email} />'
