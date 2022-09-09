from django.urls import path

from bills.bills_parser.api import BillCreate, BillList

urlpatterns = [
    path('add_bills/', BillCreate.as_view()),
    path('bills/', BillList.as_view()),
]
