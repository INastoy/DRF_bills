from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class RequiredColumnsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid columns.')
    default_code = 'invalid'


class FileTypeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Wrong file type. Expected .csv')
    default_code = 'invalid'


class UniqueTogetherError(Exception):

    def __str__(self):

        return 'client_name с таким invoice_number уже существует'


class EmptyLineError(Exception):

    def __str__(self):

        return 'Строка не содержит никаких данных'
