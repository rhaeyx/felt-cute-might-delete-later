from rest_framework.serializers import ModelSerializer

from transactions.serializers import PassSerializer

from .models import Customer


class CustomerSerializer(ModelSerializer):
    passes = PassSerializer(source="customer_passes", many=True, required=False)

    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "join_date",
            "passes",
        ]
        read_only_fields = [
            "id",
            "join_date",
        ]
