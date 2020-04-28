from abc import ABC, abstractmethod

from django.forms import ValidationError
from django.utils.translation import gettext as _

__all__ = [
    'DomainRuleMixin',
    'DeletionRuleChecker',
    'IntegrityRuleChecker',
    'RuleIntegrityError',
    'RuleInstanceTypeError',
]


class RuleValidationError(Exception):
    """
    Exceção erro em runtime para forçar validação de model no save.
    """
    pass


class RuleIntegrityError(Exception):
    """
    Exceção erro durante verificação de integridade de entidade de domínio.
    """

    def __init__(self, message, field_name: str = None, *args, **kwargs):
        self.message = message
        self.field_name = field_name
        super().__init__(*args, **kwargs)

    def __str__(self):
        return str(self.message)


class RuleDeletionError(Exception):
    """
    Exceção erro durante deleção de entidade de domínio.
    """

    def __init__(self, message, field_name: str = None, *args, **kwargs):
        self.message = message
        self.field_name = field_name
        super().__init__(*args, **kwargs)

    def __str__(self):
        return str(self.message)


class RuleInstanceTypeError(TypeError):
    """
    Exceção quando uma instância de regra de negócio de entidade informada
    mas não é instância de RuleChecker.
    """

    def __init__(self, message):
        self.message = _('The configured rule is not an instance of'
                         ' RuleChecker: {}'.format(message))


class IntegrityRuleChecker(ABC):
    """
    Classe concreta de implementação de verficação de integridade de domínio
    de uma entidade.
    :raise RuleIntegrityError
    """

    @abstractmethod
    def check(self, instance):  # pragma: no cover
        pass


class DeletionRuleChecker(ABC):
    """
    Classe concreta de implementação de deleção de entidade.
    :raise RuleIntegrityError
    """

    @abstractmethod
    def check(self, instance):  # pragma: no cover
        pass


class DomainRuleMixin:
    """
    Adds support to check domain rules
    """
    # Rule instances
    integrity_rules = list()
    deletion_rules = list()

    def __init__(self, *args, **kwargs):
        self.ignore_validation = False
        self.validation_processed = False
        self.valid = False

        integrity_rules = []

        for rule in self.integrity_rules:
            if self.is_valid_integrity_rule(rule):
                integrity_rules.append(rule)
                continue

            raise RuleInstanceTypeError(rule.__name__)

        deletion_rules = []
        for rule in self.deletion_rules:
            if self.is_valid_deletion_rule(rule):
                deletion_rules.append(rule)
                continue

            raise RuleInstanceTypeError(rule.__class__.__name__)

        if integrity_rules:
            self.integrity_rules = integrity_rules

        if deletion_rules:
            self.deletion_rules = deletion_rules

        super().__init__(*args, **kwargs)

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude, validate_unique)
        self.validate(full_clean=False)

    def validate(self, full_clean=True):
        if self.ignore_validation is False:
            self.validation_processed = True
            self._required_fields_filled()
            self._check_integrity_rules()

            if full_clean is True:
                self.full_clean()

            self.valid = True

    def delete(self, ignore_validation=False, *args, **kwargs):
        if self.ignore_validation is False and ignore_validation is False:
            self._check_deletion_rules()

        super().delete(*args, **kwargs)

    def save(self, ignore_validation=False, *args, **kwargs):
        if self.ignore_validation is False and ignore_validation is False:
            if self.validation_processed is False:
                raise RuleValidationError(
                    'Entity model must be validated before saving.'
                    ' Call .validate() before saving.'
                )

            if self.valid is False:
                raise RuleValidationError(
                    'Entity instance is not valid and cannot be saved.'
                )

        super().save(*args, **kwargs)

    @staticmethod
    def is_valid_integrity_rule(rule):
        is_subclass = issubclass(rule, IntegrityRuleChecker)
        is_instance = isinstance(rule, IntegrityRuleChecker)
        return is_subclass is True or is_instance is True

    @staticmethod
    def is_valid_deletion_rule(rule):
        is_subclass = issubclass(rule, DeletionRuleChecker)
        is_instance = isinstance(rule, DeletionRuleChecker)
        return is_subclass is True or is_instance is True

    def _required_fields_filled(self):
        """
        Check if all required fields are filled.
        """
        required_empty_fields = list()
        for f in self._meta.get_fields():
            if getattr(f, 'null', False) is True:
                continue

            if getattr(f, 'editable', True) is False:
                continue

            v = getattr(self, f.name, None)
            if v is None:
                required_empty_fields.append(f.name)

        if required_empty_fields:
            raise ValidationError(
                _('Required fields must be provided:'
                  ' {}'.format(', '.join(required_empty_fields)))
            )

    def _check_integrity_rules(self):
        """ Verifica as regras de integridade de domínio. """

        for rule in self.integrity_rules:
            if not isinstance(rule, IntegrityRuleChecker):
                rule = rule()

            try:
                rule.check(self)
            except RuleIntegrityError as e:
                msg = e.message
                if e.field_name is not None:
                    error_dict = dict()
                    error_dict[e.field_name] = msg
                    raise ValidationError(error_dict)

                raise ValidationError(msg)

    def _check_deletion_rules(self):
        """ Verifica as regras de remoção de entidade de domínio. """
        for rule in self.integrity_rules:
            if not isinstance(rule, DeletionRuleChecker):
                rule = rule()
                rule.check(self)
