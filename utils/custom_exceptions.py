from django.utils.translation import gettext_lazy
from rest_framework import status
from rest_framework.exceptions import APIException


class RequiredColumnsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy('Invalid columns.')
    default_code = 'invalid'


class UniqueTogetherError(Exception):

    def __init__(self, *args):
        pass

    def __str__(self):

        return 'client_name с таким invoice_number уже существует'
