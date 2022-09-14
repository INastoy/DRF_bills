import csv
import logging
from datetime import datetime

from rest_framework.exceptions import ValidationError
from rest_framework.parsers import BaseParser

from bills.bills_parser.models import Bill
from utils.custom_exceptions import RequiredColumnsError, UniqueTogetherError

REQUIRED_FIELDNAMES = ['client_name', 'client_org', 'date', 'service', 'sum', '№']

logger = logging.getLogger()


class CSVParser(BaseParser):
    media_type = '*/*'

    def parse(self, stream, media_type=None, parser_context=None):
        file = stream.FILES.get('file')

        if file.content_type not in ['text/csv', 'application/vnd.ms-excel']:
            raise ValidationError('Неверный формат файла. Отправьте .csv файл')
        elif file.size == 0:
            raise ValidationError('Файл пуст')

        data = file.read().decode().splitlines()
        reader: csv.DictReader = csv.DictReader(data)

        if sorted(reader.fieldnames) != REQUIRED_FIELDNAMES:
            raise RequiredColumnsError(f'Колонки {reader.fieldnames} не соответствуют требуемым: {REQUIRED_FIELDNAMES}')

        return data


def parse_reader(reader):  # TODO для больших объемов данных переехать на pandas
    data = []
    invoice_numbers = list(Bill.objects.values_list('client_name__name', 'invoice_number'))

    for num, line in enumerate(reader, start=1):

        try:
            line['invoice_number'] = float(line.pop('№'))

            if (line['client_name'], line['invoice_number']) in invoice_numbers:
                raise UniqueTogetherError()
            invoice_numbers.append((line['client_name'], (line['invoice_number'])))

            line['total'] = float(line.pop('sum'))
            line['date'] = datetime.strptime(line.pop('date'), '%d.%m.%Y').date()
            line['client_org'] = {'name': line.pop('client_org')}
            line['client_name'] = {'name': line.pop('client_name')}
            line['service'] = {'name': line.pop('service')}

            data.append(line)

        except ValueError as ex:
            logger.info(f'Неверное значение в файле  на строке {num}: {ex}')
        except TypeError as ex:
            logger.info(f'Неверный тип данных в файле на строке {num}: {ex}')
        except UniqueTogetherError as ex:
            logger.info(ex)

    return data
