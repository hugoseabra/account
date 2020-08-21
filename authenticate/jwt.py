from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as _TokenObtainPairSerializer


class TokenObtainPairSerializer(_TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(TokenObtainPairSerializer, cls).get_token(user)

        # Adding extras fields in payload
        groups = []
        for group in user.groups.all():
            groups.append(group.name)

        token.payload['meta'] = {
            'is_admin': user.is_superuser
        }
        token.payload['meta']['groups'] = groups

        return token
