from django.core.validators import MinLengthValidator
from django.db import models


class Bill(models.Model):
    client_name = models.CharField(max_length=255)
    client_org = models.CharField(max_length=255)
    number = models.IntegerField()
    total = models.FloatField()
    date = models.DateField()
    service = models.TextField(validators=[MinLengthValidator(2)])
