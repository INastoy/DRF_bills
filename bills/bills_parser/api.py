from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response

from bills.bills_parser.filters import BillFilter
from bills.bills_parser.models import Bill
from bills.bills_parser.parsers import CSVParser
from bills.bills_parser.serializers import CSVSerializer, BillSerializer
from bills.bills_parser.tasks import background_save


class BillCreate(generics.GenericAPIView):
    parser_classes = [CSVParser]
    serializer_class = CSVSerializer

    def post(self, request):

        bills = request.data
        # parse_file.delay(bills)
        background_save(bills)

        return Response('Файл успешно принят', status=status.HTTP_201_CREATED)


class BillList(generics.ListAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BillFilter
