from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions, authentication, status
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from core.util.uuid import get_validated_uuid_from_string
from core.viewsets import FieldRequestViewsetMixin
from . import serializers
from .models import User
from .models.pin import Pin


class UserViewSet(FieldRequestViewsetMixin, ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = serializers.UserSerializer.Meta.model.objects.get_queryset()

    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )


class AvatarViewSet(FieldRequestViewsetMixin, ModelViewSet):
    serializer_class = serializers.AvatarSerializer
    queryset = serializers.AvatarSerializer.Meta.model.objects.get_queryset()

    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
    http_method_names = ['get', 'post', 'delete']

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)

        if isinstance(serializer, ListSerializer) is False:
            user_pk = get_validated_uuid_from_string(
                self.kwargs.get('user_pk')
            )
            serializer.user_pk = user_pk

        return serializer

    def get_queryset(self):
        queryset = super().get_queryset()

        user_pk = get_validated_uuid_from_string(
            self.kwargs.get('user_pk')
        )

        if user_pk:
            queryset = queryset.filter(user_id=user_pk)
        else:
            queryset = queryset.none()

        return queryset

    def create(self, request, *args, **kwargs):
        user_pk = get_validated_uuid_from_string(self.kwargs.get('user_pk'))
        data = request.data.copy()
        data.update({'user_id': user_pk})

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ReadOnlySingeUserViewset(FieldRequestViewsetMixin, GenericViewSet):
    serializer_class = serializers.UserSerializer
    queryset = serializers.UserSerializer.Meta.model.objects.get_queryset()

    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )


class AccountValidationViewset(FieldRequestViewsetMixin, GenericViewSet):
    token_generator = default_token_generator

    def create(self, request, *args, **kwargs):
        uidb64 = self.kwargs.get('uidb64')
        token = self.kwargs.get('token')

        user = self.get_user(uidb64)

        if not user:
            return Response(
                data={'details': _('User was not found.')},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_validated is True:
            return Response(
                data={'details': _('User has already been validated.')},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self.token_generator.check_token(user, token) is False:
            return Response(
                data={'details': _(
                    'Link is not valid or has expired. Go to back to '
                    'account creation and try to validate the account in '
                    'less than 24 hours.'
                )},
                status=status.HTTP_404_NOT_FOUND,
            )

        pin = request.data.get('pin')

        try:
            pin = Pin.objects.get(pin=str(pin))

            if pin.is_expired is True:
                return Response(
                    data={'details': _(
                        'PIN is expired. Go to back to account creation and '
                        'try to validate the account in less than 24 hours.'
                    )},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Pin.DoesNotExist:
            return Response(
                {'details': _(
                    'PIN is invalid. Go to back to '
                    'account creation and try to validate the account in '
                    'less than 24 hours.'
                )},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            user.validate()

        return Response({
            'uidb64': uidb64,
            'user': repr(user),
            'pin': repr(pin),
            'token': token,
        })

    def get_user(self, uidb64: str) -> User:
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError,
                ValueError,
                OverflowError,
                User.DoesNotExist,
                ValidationError):
            user = None
        return user
