from django.contrib.sites.models import Site
from rest_framework import serializers

from core.serializers import FormSerializerMixin
from . import forms


class AvatarSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        form = forms.AvatarForm
        model = forms.AvatarForm.Meta.model
        fields = (
            'pk',
            'image',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_pk = None


class UserSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        form = forms.UserForm
        model = forms.UserForm.Meta.model
        fields = (
            'pk',
            'first_name',
            'last_name',
            'email',
            'cpf',
            'avatar_type',
            'created_at',
            'updated_at',
            'is_active',
            'is_superuser',
            'is_staff',
            'date_joined',
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if self.is_requested_field('avatar'):
            avatars = list()
            for a in instance.avatars.all():
                avatar_serializer = AvatarSerializer(instance=a)
                avatar_data = avatar_serializer.data
                site = Site.objects.get_current()
                avatar_data['image'] = '//{domain}{image_url}'.format(
                    domain=site.domain,
                    image_url=avatar_data['image']
                )
                avatars.append(avatar_data)

            rep['avatars'] = avatars

        return rep


class SingleUserViewSet(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        form = forms.UserForm
        model = forms.UserForm.Meta.model
        fields = (
            'pk',
            'first_name',
            'last_name',
            'email',
            'cpf',
            'avatar_type',
            'created_at',
            'updated_at',
            'is_active',
            'is_superuser',
            'is_staff',
            'date_joined',
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if self.is_requested_field('avatar'):
            avatars = list()
            for a in instance.avatars.all():
                avatar_serializer = AvatarSerializer(instance=a)
                avatar_data = avatar_serializer.data
                site = Site.objects.get_current()
                avatar_data['image'] = '//{domain}{image_url}'.format(
                    domain=site.domain,
                    image_url=avatar_data['image']
                )
                avatars.append(avatar_data)

            rep['avatars'] = avatars

        return rep
