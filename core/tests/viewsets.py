import json
from datetime import datetime, timedelta
from uuid import UUID

from django.apps import apps
from django.contrib.sites.models import Site

"""
CONFIGURAÇÃO:
-------------
Campos obrigatórios com valores iniciais
Campos não obrigatórios com valores iniciais
Campos relacionais obrigatórios (valor automatizado)
Campos relacionais não obrigatórios (valor automatizado)

TESTES:
-------
- Chave de primary key (pk, ou id ou uuid)
- Criação somente campos obrigatórios
- Criação com todos os campos
- Edição somente com campos obrigatórios
- Edição com todos os campos obrigatórios
- Edição parcial campo a campo (todos os campos)
- Exclusão de registro

- Retorno de schema contém campos obrigatórios
- Campos relacionais obrigatórios com pk direto
- Campos relacionais obrigatórios com dict incluindo pk
- Retorno de erro se não houver campos obrigatórios
"""


class CRUDEndpointTestMixin:
    """
    Testes de API - CRUD
    """
    model = ''
    create_endpoint = ''
    item_endpoint = ''
    pk_name = ''
    required_fields = {}
    other_fields = {}
    required_fk_fields = ()
    other_fk_fields = ()

    fixtures = [
        '000_site_dev'
    ]

    def _get_model_class(self):
        """
        Get a model.

        :param name String on the form 'applabel.modelname' or 'modelname'.
        :return a model class.
        """
        if '.' not in self.model:
            raise Exception('Provide model name using app_label.model_name')

        app_label, model_name = self.model.split('.')
        return apps.get_model(app_label, model_name)

    def _get_keys(self):
        keys = list(self.required_fields.keys())
        keys += list(self.other_fields.keys())
        return keys

    def _get_full_data(self) -> dict:
        data = self.required_fields.copy()
        data.update(self.other_fields.copy())
        return data

    def get_full_uri(self, endpoint):
        site = Site.objects.get_current()
        domain = site.domain
        domain = domain.rtrim('/') if str(domain).endswith('/') else domain
        return 'http://{}{}'.format(domain, endpoint)

    def _test_endpoint_creation(self, all_fields=False):
        uri = self.get_full_uri(self.create_endpoint)

        if all_fields is True:
            data = self._get_full_data()
        else:
            data = self.required_fields

        result = self.client.post(
            path=uri,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(result.status_code, 201)
        return result.data

    def _test_pk_in_schema(self, data):
        self.assertIn(self.pk_name, data)

    def _test_endpoint_response_schema(self, data):
        """
        Testa scheme que retorna da resposta do endpoint que deve se igual
        à junção dos campos obrigatórios e não obrigatórios
        """
        keys = self._get_keys()
        keys.append(self.pk_name)
        self.assertListEqual(sorted(keys), sorted(list(data.keys())))

    def _test_pk_exists(self, pk):
        model_class = self._get_model_class()
        self.assertTrue(model_class.objects.filter(pk=pk).exists())

    def _create_sample_record(self):
        raise NotImplementedError()

    def test_item_creation_with_required_fields(self):
        """
        Testa criação de item, passando pelas seguintes validações:
        - testa criação pelo endoint somente com campos obrigatórios
        - testa se PK existe no schema de retorno
        - testa se campos obrigatórios e não obrigatórios existem no retorno
        - testa se PK de retorno foi persistido
        """
        data = self._test_endpoint_creation(all_fields=False)
        self._test_pk_in_schema(data)
        pk = data.get(self.pk_name)

        self._test_endpoint_response_schema(data)
        self._test_pk_exists(pk)

    def test_item_creation_with_all_fields(self):
        """
        Testa criação de item, passando pelas seguintes validações:
        - testa criação pelo endoint com todos os campos
        - testa se PK existe no schema de retorno
        - testa se campos obrigatórios e não obrigatórios existem no retorno
        - testa se PK de retorno foi persistido
        """
        data = self._test_endpoint_creation(all_fields=True)
        self._test_pk_in_schema(data)
        pk = data.get(self.pk_name)

        self._test_endpoint_response_schema(data)
        self._test_pk_exists(pk)

    def test_item_creation_with_required_field_errors(self):
        """
        Testa erro de criação de item não informando um dos campos
        obrigatórios:
        - testa erro de criação campo a campo obrigatório
        """
        uri = self.get_full_uri(self.create_endpoint)

        for k in self.required_fields.keys():
            required_fields = self.required_fields.copy()
            del required_fields[k]

            result = self.client.post(
                path=uri,
                data=json.dumps(required_fields),
                content_type='application/json',
            )
            self.assertEqual(result.status_code, 400)
            serializer = result.data.serializer
            self.assertIn(k, serializer.errors)

    def test_item_retrieve(self):
        """
        Testa criação de item, passando pelas seguintes validações:
        - testa resgate de dados pelo endoint
        - testa se campos obrigatórios e não obrigatórios existem no retorno
        """
        sample_item = self._create_sample_record()
        endpoint = self.item_endpoint.format(pk=sample_item.pk)

        uri = self.get_full_uri(endpoint)
        result = self.client.get(
            path=uri,
            content_type='application/json',
        )
        self.assertEqual(result.status_code, 200)

        data = result.data

        self._test_endpoint_response_schema(data)

    def test_item_edition_full_data(self):
        """
        Testa edição de item com todos os campos, usando PUT
        """
        sample_item = self._create_sample_record()

        data = self._get_full_data()

        ignore_fields = [
            'pk',
            'created_at',
            'updated_at',
        ]

        for field_name, value in sample_item.get_values().items():
            if field_name in ignore_fields:
                continue

            if isinstance(value, str):
                value = value[:25] + '-edited'
            elif isinstance(value, bool):
                value = False if value is True else True
            elif isinstance(value, datetime):
                value = value + timedelta(minutes=10)
                value = value.strftime('%Y-%m-%dT%H:%M:%S%z')
            elif isinstance(value, int):
                value = value + 1
            elif isinstance(value, UUID):
                value = str(value)

            data[field_name] = value

        endpoint = self.item_endpoint.format(pk=sample_item.pk)

        result = self.client.put(
            path=self.get_full_uri(endpoint),
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(result.status_code, 200)

        # Resgata da persistência novo registro
        item = self._get_model_class().objects.get(pk=sample_item.pk)

        for k, v in data.items():
            self.assertEqual(v, getattr(item, k))

    def test_item_edition_partial_data(self):
        """
        Testa edição de item campo a campo, usando PATCH
        """
        sample_item = self._create_sample_record()

        endpoint = self.item_endpoint.format(pk=sample_item.pk)

        ignore_fields = [
            'pk',
            'created_at',
            'updated_at',
        ]

        for field_name, value in sample_item.get_values().items():
            if field_name in ignore_fields:
                continue

            if isinstance(value, str):
                value = value[:25] + '-edited'
            elif isinstance(value, bool):
                value = False if value is True else True
            elif isinstance(value, datetime):
                value = value + timedelta(minutes=10)
                value = value.strftime('%Y-%m-%dT%H:%M:%S%z')
            elif isinstance(value, int):
                value = value + 1
            elif isinstance(value, UUID):
                value = str(value)

            result = self.client.patch(
                path=self.get_full_uri(endpoint),
                data=json.dumps({field_name: value}),
                content_type='application/json',
            )

            self.assertEqual(result.status_code, 200)

    def test_item_deletion(self):
        """
        Teste exclusão de registro por endpoint
        """
        sample_item = self._create_sample_record()
        endpoint = self.item_endpoint.format(pk=sample_item.pk)

        uri = self.get_full_uri(endpoint)
        result = self.client.delete(
            path=uri,
            content_type='application/json',
        )
        self.assertEqual(result.status_code, 204)

        with self.assertRaises(sample_item.__class__.DoesNotExist):
            model_class = self._get_model_class()
            model_class.objects.get(pk=sample_item.pk)
