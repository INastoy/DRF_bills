import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional

from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bills.bills_parser.models import Bill, Client, Organization, Service

logger = logging.getLogger()


@dataclass
class BulkCreateData:
    clients: Optional[list[Client]] = field(default_factory=list)
    organizations: list[Organization] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)


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

    def to_internal_value(self, data):
        """
        Метод is_valid() при обработке списка сущностей вернет все удачно валидированные сущности в validated_data,
        а неудачно - в errors
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

    def create(self, validated_data):
        """
        Bulk create a bills and all parent models (Client, Organization etc) if it's needed.
        """
        bulk_create_data = BulkCreateData()
        self._prepare_for_bulk_create(bulk_create_data, validated_data)

        bills = [self.child.create(attrs) for attrs in validated_data]

        try:
            self._cascade_bulk_create(bills, bulk_create_data)
            logger.info(f'Успешно созданы счета: {bills}')
        except IntegrityError as e:
            logger.error(f'При создании счетов получена ошибка: {e}. Список счетов: {bills}')

        return bills

    @transaction.atomic()
    def _cascade_bulk_create(self, bills, bulk_create_data):
        Client.objects.bulk_create(bulk_create_data.clients)
        Organization.objects.bulk_create(bulk_create_data.organizations)
        Service.objects.bulk_create(bulk_create_data.services)
        self.child.Meta.model.objects.bulk_create(bills)

    def _prepare_for_bulk_create(self, bulk_create_data: BulkCreateData, validated_data: dict):
        clients = list(Client.objects.all().only('pk', 'name'))
        organizations = list(Organization.objects.all().only('pk', 'name'))
        services = list(Service.objects.all().only('pk', 'name'))
        for bill in validated_data:
            bill['client_id'] = self._get_client_pk(bill, clients, bulk_create_data.clients)
            bill['client_org_id'] = self._get_client_org_pk(bill, organizations, bulk_create_data.organizations)
            bill['service_id'] = self._get_service_pk(bill, services, bulk_create_data.services)
            bill['id'] = uuid.uuid4()

    @staticmethod
    def _get_client_pk(bill: dict, clients: list[Client], clients_for_create: list):
        client_name = bill['client']['name']
        for client in clients:
            if client_name == client.name:
                return str(client.id)
        client_for_create = Client(id=uuid.uuid4(), name=client_name)
        clients.append(client_for_create)
        clients_for_create.append(client_for_create)
        return str(client_for_create.id)

    @staticmethod
    def _get_client_org_pk(bill: dict, organizations: list[Organization], organizations_for_create: list):
        client_org_name = bill['client_org']['name']
        for org in organizations:
            if client_org_name == org.name:
                return str(org.id)
        org_for_create = Organization(id=uuid.uuid4(), name=client_org_name, client_id=bill.get('client_id'))
        organizations.append(org_for_create)
        organizations_for_create.append(org_for_create)
        return str(org_for_create.id)

    @staticmethod
    def _get_service_pk(bill: dict, services: list[Service], services_for_create: list):
        service_name = bill['service']['name']
        for service in services:
            if service_name == service.name:
                return str(service.id)
        service_for_create = Service(id=uuid.uuid4(), name=service_name)
        services.append(service_for_create)
        services_for_create.append(service_for_create)
        return str(service_for_create.id)


class BillSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    client_org = OrganizationSerializer()
    service = ServiceSerializer()

    def create(self, validated_data):
        instance = Bill(
            id=validated_data['id'],
            client_id=validated_data['client_id'],
            client_org_id=validated_data['client_org_id'],
            service_id=validated_data['service_id'],
            invoice_number=validated_data['invoice_number'],
            total=validated_data['total'],
            date=validated_data['date'],
        )
        return instance

    class Meta:
        model = Bill
        fields = '__all__'
        list_serializer_class = BulkCreateBillSerializer
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Bill.objects.all(),
        #         fields=['client_id', 'invoice_number']
        #     )
        # ]
