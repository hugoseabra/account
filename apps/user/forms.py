from django import forms
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .models import User, Avatar


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("email", 'cpf',)


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'cpf',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_new = self.instance.is_new is True

    def clean(self):
        self.set_existing_user()
        return super().clean()

    def set_existing_user(self):
        if self.is_new is True:
            email = self.cleaned_data['email']
            cpf = self.cleaned_data['cpf']
            users = User.objects.filter(
                Q(email=email) | Q(cpf=cpf)
            )

            # One or more users
            if users:
                if len(users) > 1:
                    # Multiple users means that CPF and e-mail are from
                    # different users.
                    self.add_error(None, _(
                        'Users with the provided'
                        ' e-mail or CPF already exists.'
                    ))
                    return

                user = users[0]

                # So, the new user already exists. Let's assume
                # the existing one
                self.instance = user

        if self.instance.is_active is False:
            # User was deactivated administratively.
            self.add_error(None, _(
                'This user is not allowed. Get in touch with support'
                ' for further information.'
            ))
            return

        # Existing user is the same for CPF and email
        # it is active


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Avatar
        fields = '__all__'
