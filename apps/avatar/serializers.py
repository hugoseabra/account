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
            'type',
            'image',
            'created_at',
            'updated_at',
        )
