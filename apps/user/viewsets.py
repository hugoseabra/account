from rest_framework import permissions, authentication
from rest_framework.viewsets import ModelViewSet

from core.viewsets import FieldRequestViewsetMixin
from . import serializers


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
