from copy import copy

from django.core.files import File
from django.db.models import Model
from django.forms.models import model_to_dict
from rest_framework import serializers
from rest_framework.fields import empty

from .fields_serializer_mixin import FieldsSerializerMixin


class FormSerializerMixin(FieldsSerializerMixin):
    class Meta:
        form = None

    pk_possible_keys = ['uuid', 'pk', 'id']

    def __init__(self, *args, **kwargs):
        self.instance = None
        self.form_instance = None
        super().__init__(*args, **kwargs)

    def run_validation(self, data=empty):
        return super().run_validation(data=self.partial_update_data(data))

    def partial_update_data(self, data=empty):
        if self.partial is False or not self.instance or data is empty:
            return data

        data = copy(data)

        for k, v in model_to_dict(self.instance).items():
            if k not in data:
                data[k] = v

        for k, v in data.items():
            if isinstance(v, dict) and 'pk' in v:
                v = v.get('pk')

            data.update({k: v})

        return data

    def normalize_data(self, data):
        for k, v in data.items():
            if isinstance(v, dict) is False:
                continue

            for pk_key in self.pk_possible_keys:
                if pk_key in v and v[pk_key]:
                    data[k] = v[pk_key]
                    break

        return data

    def to_internal_value(self, data: dict):
        data = self.normalize_data(data)
        return super().to_internal_value(data)

    def validate(self, data):

        form_data = data
        files = dict()

        for name, item in form_data.items():
            if item and isinstance(item, Model):
                form_data[name] = item.pk

            if item and isinstance(item, File):
                files[name] = item

        self.form_instance = self.get_form(data=form_data, files=files)

        if not self.form_instance.is_valid():
            raise serializers.ValidationError(
                {'errors': self.form_instance.errors}
            )
        else:
            cleaned_data = self.form_instance.cleaned_data

        return cleaned_data

    def get_form(self, data=None, files=None, **kwargs):
        """
        Returns an instance of the form to be used in this view.
        """

        assert hasattr(self, 'Meta'), (
            'Class {form_serializer_class} missing '
            '"Meta" class'.format(
                form_serializer_class=self.__class__.__name__
            )
        )

        assert hasattr(self.Meta, 'form'), (
            'Class {form_serializer_class} missing '
            '"Meta.form" attribute'.format(
                form_serializer_class=self.__class__.__name__
            )
        )

        if self.instance:
            kwargs['instance'] = self.instance

        if not self.form_instance:
            self.form_instance = self.Meta.form(data=data,
                                                files=files,
                                                **kwargs)

        return self.form_instance

    # def to_internal_value(self, data):
    #     pass

    def save(self, **_):
        assert self.form_instance is not None
        self.instance = self.form_instance.save(True)
        return self.instance
