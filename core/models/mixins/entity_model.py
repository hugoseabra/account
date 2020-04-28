from django.db import models

from core.models.mixins import AuditableMixin
from core.models.mixins import DeletableModelMixin
from core.models.mixins import EntityMixin
from core.models.mixins import UUIDPkMixin


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
