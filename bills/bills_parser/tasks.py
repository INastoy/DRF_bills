import csv
import logging

from celery import shared_task

from bills.bills_parser.parsers import parse_reader
from bills.bills_parser.serializers import BillSerializer

logger = logging.getLogger()


@shared_task()
def parse_file(bills):
    reader: csv.DictReader = csv.DictReader(bills)
    parsed_data = parse_reader(reader)

    bill_serializer = BillSerializer(data=parsed_data, many=True)
    bill_serializer.is_valid() # Стандартное поведение метода to_internal_value() переопределено см. serializers.py
    bill_serializer.save()
