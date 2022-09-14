import logging

from django.db import IntegrityError
from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bills.bills_parser.models import Bill, Client, Organization, Service

logger = logging.getLogger()


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class CSVSerializer(serializers.Serializer):
    file = serializers.FileField()


class BulkCreateBillSerializer(serializers.ListSerializer):

    def name_to_pk(self, data: list, queryset: QuerySet, column_name: str):
        new_objects = []
        last_created_obj = ''
        for num, line in enumerate(data):
            name = line.get(column_name).get('name')
            if queryset.filter(name=name):
                data[num][f'{column_name}_id'] = queryset.get(name=name).id
                data[num].pop(column_name)
            elif name in new_objects:
                data[num][f'{column_name}_id'] = last_created_obj.id
                data[num].pop(column_name)
            else:
                new_objects.append(name)
                if queryset.model == Organization:
                    last_created_obj = Organization.objects.create(name=name, client_id=line['client_name_id'])
                else:
                    last_created_obj = queryset.model.objects.create(name=name)  # TODO Переписать на bulk_create
                data[num][f'{column_name}_id'] = last_created_obj.id
                data[num].pop(column_name)

    def create(self, validated_data):
        clients = Client.objects.all().only('pk', 'name')  # TODO Принудительно выполнять запросы
        self.name_to_pk(validated_data, clients, 'client_name')
        organizations = Organization.objects.all().only('pk', 'name')
        self.name_to_pk(validated_data, organizations, 'client_org')
        services = Service.objects.all().only('pk', 'name')
        self.name_to_pk(validated_data, services, 'service')

        result = [self.child.create(attrs) for attrs in validated_data]

        try:
            self.child.Meta.model.objects.bulk_create(result)
            logger.info(f'Успешно созданы счета: {result}')
        except IntegrityError as e:
            logger.error(f'При создании счетов получена ошибка: {e}. Список счетов: {result}')

        return result

    def to_internal_value(self, data):
        """
        Метод is_valid() теперь возвращает удачно валидированные данные даже при возникновении ошибок во время валидации
        """
        ret = []
        errors = []

        for item in data:
            try:
                validated = self.child.run_validation(item)
            except ValidationError as exc:
                errors.append(exc.detail)
            else:
                ret.append(validated)
        if errors:
            logger.info(f'Ошибки во время валидации сериалайзером: {errors}')

        return ret


class BillSerializer(serializers.ModelSerializer):
    client_name = ClientSerializer()
    client_org = OrganizationSerializer()
    service = ServiceSerializer()

    def create(self, validated_data):
        instance = Bill(**validated_data)

        return instance

    class Meta:
        model = Bill
        fields = '__all__'
        list_serializer_class = BulkCreateBillSerializer
