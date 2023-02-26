import uuid

from django.core.validators import MinLengthValidator
from django.db import models


class Service(models.Model):
    id = models.UUIDField(primary_key=True, null=False, unique=True, default=uuid.uuid4(), blank=True)
    name = models.CharField(max_length=255, validators=[MinLengthValidator(2)])


class Client(models.Model):
    id = models.UUIDField(primary_key=True, null=False, unique=True, default=uuid.uuid4(), blank=True)
    name = models.CharField(max_length=255)


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, null=False, unique=True, default=uuid.uuid4(), blank=True)
    name = models.CharField(max_length=255)
    client = models.ForeignKey(to=Client, on_delete=models.PROTECT, blank=True)


class Bill(models.Model):
    id = models.UUIDField(primary_key=True, null=False, unique=True, default=uuid.uuid4(), blank=True)
    client = models.ForeignKey(to=Client, on_delete=models.PROTECT)
    client_org = models.ForeignKey(to=Organization, on_delete=models.PROTECT)
    invoice_number = models.IntegerField()
    total = models.FloatField()
    date = models.DateField()
    service = models.ForeignKey(to=Service, on_delete=models.PROTECT)

    class Meta:
        unique_together = ['client_id', 'invoice_number']
