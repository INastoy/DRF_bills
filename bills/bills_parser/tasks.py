import csv
import logging
from datetime import datetime
from typing import TypedDict

from celery import shared_task

from bills.bills_parser.models import Bill
from bills.bills_parser.serializers import BillSerializer
from utils.custom_exceptions import UniqueTogetherError, EmptyLineError

logger = logging.getLogger()


class BillType(TypedDict):

    client: dict
    client_org: dict
    invoice_number: float
    total: float
    date: datetime.date
    service: dict


@shared_task()
def background_save(bills):
    reader: csv.DictReader = csv.DictReader(bills)
    parsed_data = _parse_reader(reader)

    bill_serializer = BillSerializer(data=parsed_data, many=True)
    bill_serializer.is_valid()  # Стандартное поведение метода to_internal_value() переопределено см. serializers.py
    bill_serializer.save()


def _parse_reader(reader: csv.DictReader) -> list[BillType]:
    data = []
    for num, line in enumerate(reader, start=2):
        if not is_valid(line):
            continue
        try:
            bill = BillType(
                    invoice_number=_get_invoice_number(line),
                    total=_get_total(line),
                    date=_get_date(line),
                    client_org=_get_client_org(line),
                    client=_get_client(line),
                    service=_get_service(line),
            )
            data.append(bill)

        except ValueError as ex:
            logger.info(f'Ошибка {ex}  на строке номер {num}')
        except TypeError as ex:
            logger.info(f'Неверный тип данных в файле на строке {num}: {ex}')

    return data


def is_valid(line: dict) -> bool:
    try:
        _is_empty_line(line)
        _check_unique_together(line)
    except UniqueTogetherError as ex:
        logger.debug(ex)
        return False
    except EmptyLineError as ex:
        logger.debug(ex)
        return False
    return True


def _check_unique_together(line: dict) -> None:
    invoice_numbers = list(
        Bill.objects.select_related('client').values_list('client__name', 'invoice_number')
    )

    client_name = line['client_name']
    invoice_number = int(line['№'])
    if (client_name, invoice_number) in invoice_numbers:
        raise UniqueTogetherError()
    invoice_numbers.append((client_name, invoice_number))


def _is_empty_line(line: dict) -> bool:
    for val in line.values():
        if val:
            return False
    raise EmptyLineError


def _get_invoice_number(line: dict) -> float:
    return float(line.get('№'))


def _get_total(line: dict) -> float:
    total = line.get('sum').replace(',', '.')
    return float(total)


def _get_date(line: dict) -> datetime.date:
    return datetime.strptime(line.get('date'), '%d.%m.%Y').date()


def _get_client_org(line: dict) -> dict:
    return {'name': line.get('client_org')}


def _get_client(line: dict) -> dict:
    return {'name': line.get('client_name')}


def _get_service(line: dict) -> dict:
    return {'name': line.get('service')}
