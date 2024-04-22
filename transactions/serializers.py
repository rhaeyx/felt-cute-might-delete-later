from rest_framework.serializers import ModelSerializer

from .models import Package, Pass, Transaction


class PackageSerializer(ModelSerializer):
    class Meta:
        model = Package
        fields = ["id", "name", "description", "price", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at"]


class PassSerializer(ModelSerializer):
    class Meta:
        model = Pass
        fields = [
            "id",
            "code",
            "time_left",
            "created_at",
            "expires_at",
            "updated_at",
            "customer",
            "package",
            "staff",
        ]
        read_only_fields = ["id"]


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "time_in",
            "time_out",
            "amount",
            "package",
            "customer",
            "staff",
            "used_pass",
            "time_consumed",
            "is_complete",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "udpated_at",
            "is_complete",
            "time_consumed",
        ]
