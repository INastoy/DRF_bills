import csv
import logging

from rest_framework.exceptions import ValidationError
from rest_framework.parsers import BaseParser

from utils.custom_exceptions import RequiredColumnsError, FileTypeError

REQUIRED_FIELDNAMES = ['client_name', 'client_org', 'date', 'service', 'sum', '№']

logger = logging.getLogger()


class CSVParser(BaseParser):
    media_type = 'multipart/form-data'

    def parse(self, stream, media_type=None, parser_context=None):
        file = stream.FILES.get('file')
        self._validate_file(file)

        data = file.read().decode().splitlines()
        reader: csv.DictReader = csv.DictReader(data)
        self._is_required_columns_exists(reader)

        return data

    @staticmethod
    def _is_required_columns_exists(reader):
        for field in REQUIRED_FIELDNAMES:
            if field not in reader.fieldnames:
                raise RequiredColumnsError(
                    f'Колонки {reader.fieldnames} не соответствуют требуемым: {REQUIRED_FIELDNAMES}'
                )

    @staticmethod
    def _validate_file(file):
        if file.content_type not in ['text/csv', 'application/vnd.ms-excel']:
            raise FileTypeError('Неверный формат файла. Отправьте .csv файл')
        elif file.size == 0:
            raise ValidationError('Файл пуст')
