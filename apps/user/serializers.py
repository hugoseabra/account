from rest_framework import serializers

from core.serializers import FormSerializerMixin
from . import forms


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
