class EntityMixin:
    """
    Mixin to add utilities to model
    """

    @property
    def is_new(self):
        return self._state.adding is True

    def get_pk_name(self):
        return self._meta.pk.name

    def get_fields(self, include_hidden=True) -> dict:
        fields = dict()
        for f in self._meta.get_fields(include_hidden=include_hidden):
            name = f.name
            if f.name == self.get_pk_name():
                name = 'pk'
            fields[name] = f
        return fields

    def get_values(self, include_hidden=True) -> dict:
        values = dict()
        for f in self._meta.get_fields(include_hidden=include_hidden):
            name = f.name
            if f.name == self.get_pk_name():
                name = 'pk'

            if f.is_relation is True:
                continue
            values[name] = getattr(self, name)
        return values

    def get_field(self, field_name: str):
        return self._meta.get_field(field_name)
