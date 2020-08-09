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
            'created_at',
            'updated_at',
        )
