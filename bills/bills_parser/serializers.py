from rest_framework import serializers

from bills.bills_parser.models import Bill


class CSVSerializer(serializers.Serializer):
    file = serializers.FileField()


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'
