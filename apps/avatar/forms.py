from django import forms

from apps.avatar.models import Avatar


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Avatar
        fields = '__all__'
