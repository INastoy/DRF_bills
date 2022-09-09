import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response

from bills.bills_parser.models import Bill
from bills.bills_parser.parsers import CSVParser
from bills.bills_parser.serializers import CSVSerializer, BillSerializer

logger = logging.getLogger()


class BillCreate(generics.GenericAPIView):
    parser_classes = [CSVParser]
    serializer_class = CSVSerializer

    def post(self, request):
        bills = request.data.copy()
        for bill in bills:
            bill_serializer = BillSerializer(data=bill)
            if bill_serializer.is_valid():
                pass
                bill_serializer.save()
            else:
                logger.info(f'Ошибка валидации на строке {bill}')
        return Response(bills, status=status.HTTP_201_CREATED)


class BillList(generics.ListAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['client_name', 'client_org']
