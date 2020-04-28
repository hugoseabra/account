from django.db import models

from .mixins import AuditableMixin
from .mixins import DeletableModelMixin
from .mixins import EntityMixin
from .mixins import UUIDPkMixin


class EntityModelMixin(UUIDPkMixin,
                       AuditableMixin,
                       EntityMixin,
                       DeletableModelMixin,
                       models.Model):
    """
    Parent class for entity models.
    """
    class Meta:
        abstract = True
