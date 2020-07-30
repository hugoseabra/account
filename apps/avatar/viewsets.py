from rest_framework import permissions, authentication
from rest_framework.viewsets import ModelViewSet

from core.viewsets import FieldRequestViewsetMixin
from . import serializers


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
