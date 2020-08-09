from rest_framework_nested import routers

from apps.user import viewsets
from apps.user.viewsets import AvatarViewSet

router = routers.DefaultRouter()

router.register('me', viewsets.ReadOnlySingeUserViewset, basename='me')
router.register('users', viewsets.UserViewSet)

# User
user_router = routers.NestedSimpleRouter(
    parent_router=router,
    parent_prefix='users',
    lookup='user'
)
user_router.register(
    prefix='avatars',
    viewset=AvatarViewSet,
    basename='avatar'
)

urlpatterns = router.urls
urlpatterns += user_router.urls
