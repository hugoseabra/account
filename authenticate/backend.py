from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


UserModel = get_user_model()


class ModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        # username_field = UserModel.USERNAME_FIELD
        #
        # if username is None:
        #     username = kwargs.get(username_field)
        # if username is None or password is None:
        #     return
        # try:
        #     if request.resolver_match.app_name in ['admin']:
        #         user = UserModel._default_manager.get_by_natural_key(username)
        #     else:
        #         user = UserModel.site_manager.get(**{username_field: username})
        # except UserModel.DoesNotExist:
        #     # Run the default password hasher once to reduce the timing
        #     # difference between an existing and a nonexistent user (#20760).
        #     UserModel().set_password(password)
        # else:
        #     if user.check_password(password) and self.user_can_authenticate(user):
        #         return user

        return super().authenticate(request, username, password, **kwargs)
