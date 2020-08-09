from django.urls import path
from rest_framework_nested import routers

from apps.user import viewsets

router = routers.DefaultRouter()

pin_urls = [
    path(
        'validations/<uidb64>/<token>/',
        viewsets.AccountValidationViewset.as_view({
            'post': 'create'
        }),
        name='pin-validations'
    ),
]

urlpatterns = pin_urls
