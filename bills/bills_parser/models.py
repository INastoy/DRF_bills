from django.core.validators import MinLengthValidator
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=255, validators=[MinLengthValidator(2)])


class Client(models.Model):
    name = models.CharField(max_length=255)


class Organization(models.Model):
    name = models.CharField(max_length=255)
    client = models.ForeignKey(to=Client, on_delete=models.PROTECT, blank=True)


class Bill(models.Model):
    client_name = models.ForeignKey(to=Client, on_delete=models.PROTECT)
    client_org = models.ForeignKey(to=Organization, on_delete=models.PROTECT)
    invoice_number = models.IntegerField()
    total = models.FloatField()
    date = models.DateField()
    service = models.ForeignKey(to=Service, on_delete=models.PROTECT)

    class Meta:
        unique_together = ['client_name_id', 'invoice_number']
