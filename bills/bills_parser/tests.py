from datetime import date
from time import sleep

from django.urls import reverse
from rest_framework import test, status

from bills.bills_parser.models import Bill, Client, Organization, Service
from bills.bills_parser.serializers import BillSerializer


class BillsListAPITestCase(test.APITestCase):
    def setUp(self):
        self.url = reverse('bills')
        self.client_1 = Client.objects.create(name='test_client_1')
        self.client_2 = Client.objects.create(name='test_client_2')
        self.org_1 = Organization.objects.create(name='test_org_1', client=self.client_1)
        self.org_2 = Organization.objects.create(name='test_org_2', client=self.client_1)
        self.org_3 = Organization.objects.create(name='test_org_2', client=self.client_2)
        self.service_1 = Service.objects.create(name='test_service_1')
        self.service_2 = Service.objects.create(name='test_service_2')
        self.bill_1 = Bill.objects.create(client_name=self.client_1, client_org=self.org_1, service=self.service_1,
                                          total=15000.0, invoice_number=1, date=date(2021, 4, 1))
        self.bill_2 = Bill.objects.create(client_name=self.client_1, client_org=self.org_1, service=self.service_1,
                                          total=16000.0, invoice_number=2, date=date(2021, 4, 2))
        self.bill_3 = Bill.objects.create(client_name=self.client_1, client_org=self.org_2, service=self.service_2,
                                          total=17000.0, invoice_number=3, date=date(2021, 4, 3))
        self.bill_4 = Bill.objects.create(client_name=self.client_2, client_org=self.org_3, service=self.service_1,
                                          total=18000.0, invoice_number=1, date=date(2021, 4, 4))

    def test_get_list(self):
        response = self.client.get(self.url)
        bills = Bill.objects.all()
        serializer_data = BillSerializer(bills, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filtered_by_name_list(self):
        response = self.client.get(self.url, data={'client_name__name': 'test_client_1'})
        bills = Bill.objects.filter(client_name__name='test_client_1').all()
        serializer_data = BillSerializer(bills, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filtered_by_id_list(self):
        response = self.client.get(self.url, data={'client_org': self.org_1.id})
        bills = Bill.objects.filter(client_org=self.org_1.id).all()
        serializer_data = BillSerializer(bills, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


class BillsAPITestCase(test.APITestCase):
    def setUp(self):
        self.url = reverse('add_bills')
        self.bills_count = Bill.objects.count()

    # def test_create_bills_ok(self): # TODO Подружить тесты с Селери
    #     self.assertEqual(self.bills_count, Bill.objects.count())
    #     with open('utils/for_tests/bills_ok.csv', 'r', encoding='utf8') as file:
    #         data = {'file': file}
    #         response = self.client.post(self.url, data=data)
    #         self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    #         self.assertEqual(self.bills_count + 22, Bill.objects.count())

    def test_create_bills_empty_file(self):
        self.assertEqual(self.bills_count, Bill.objects.count())
        with open('utils/for_tests/bills_empty.csv', 'r', encoding='utf8') as file:
            data = {'file': file}
            response = self.client.post(self.url, data=data)
            self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
            self.assertEqual(self.bills_count, Bill.objects.count())

    def test_create_bills_wrong_file_type(self):
        self.assertEqual(self.bills_count, Bill.objects.count())
        with open('utils/for_tests/bills_wrong_file_type.xlsx', 'rb') as file:
            data = {'file': file}
            response = self.client.post(self.url, data=data)
            self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
            self.assertEqual(self.bills_count, Bill.objects.count())
    #
    # def test_create_bills_partial_ok(self):
    #     self.assertEqual(self.bills_count, Bill.objects.count())
    #     with open('utils/for_tests/bills_partial_ok.csv', 'r', encoding='utf8') as file:
    #         data = {'file': file}
    #         response = self.client.post(self.url, data=data)
    #         self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    #         self.assertEqual(self.bills_count + 1, Bill.objects.count())

    def test_wrong_columns_name(self):
        with open('utils/for_tests/bills_wrong_columns.csv', 'rb') as file:
            data = {'file': file}
            response = self.client.post(self.url, data=data)
            self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
            self.assertEqual(self.bills_count, Bill.objects.count())

    # def test_stress_test(self):
    #     self.assertEqual(self.bills_count, Bill.objects.count())
    #     with open('utils/for_tests/bills_stress_test.csv', 'r', encoding='utf8') as file:
    #         data = {'file': file}
    #         response = self.client.post(self.url, data=data)
    #         self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    #         print(Bill.objects.count())
    #         print(self.bills_count)
    #         sleep(2)
    #         self.assertEqual(self.bills_count + 50, Bill.objects.count())
