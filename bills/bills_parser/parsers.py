import csv
import logging
from datetime import datetime

from rest_framework.exceptions import ValidationError
from rest_framework.parsers import BaseParser

logger = logging.getLogger()


class CSVParser(BaseParser):
    media_type = '*/*'

    def parse_reader(self, reader):
        data = []
        for num, line in enumerate(reader, start=1):
            try:
                line['number'] = float(line.pop('№'))
                line['total'] = float(line.pop('sum'))
                line['date'] = datetime.strptime(line.pop('date'), '%d.%m.%Y').date()
                data.append(line)

            except ValueError as ex:
                logger.info(f'Неверное значение в файле на строке {num}: {ex}')
            except TypeError as ex:
                logger.info(f'Неверный тип данных в файле на строке {num}: {ex}')

        return data

    def parse(self, stream, media_type=None, parser_context=None):
        file = stream.FILES.get('file')
        if file.content_type != 'text/csv':
            raise ValidationError('Неверный формат файла. Отправьте .xlsx файл')
        reader: csv.DictReader = csv.DictReader(file.read().decode().splitlines())
        parsed_data = self.parse_reader(reader)

        return parsed_data


