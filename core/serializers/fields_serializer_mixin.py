class FieldsSerializerMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fields = self.get_requested_fields()
        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            for field_name in set(self.field_names) - set(fields):
                self.fields.pop(field_name)

        excluded_fields = self.get_excluded_fields()
        if excluded_fields:
            for f in self.field_names:
                if f not in excluded_fields:
                    continue
                self.fields.pop(f)

    @property
    def field_names(self):
        return list(self.fields.keys())

    def has_field(self, field_name):
        return field_name in self.field_names

    def get_excluded_fields(self):
        return self.context.get('excluded_fields')

    def get_requested_fields(self):
        excluded_fields = self.get_excluded_fields() or list()
        return [
            f
            for f in self.context.get('fields', list())
            if f not in excluded_fields
        ]

    def has_requested_fields(self):
        return self.get_requested_fields() != []

    def is_requested_field(self, field_name):
        if self.has_requested_fields() is False:
            return True

        return field_name in self.get_requested_fields()
