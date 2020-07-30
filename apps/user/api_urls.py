from rest_framework_nested import routers

from . import viewsets

router = routers.DefaultRouter()

router.register('users', viewsets.UserViewSet)

urlpatterns = router.urls

