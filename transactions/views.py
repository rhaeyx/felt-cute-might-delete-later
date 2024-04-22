from datetime import timedelta

from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .helpers import *
from .models import Package, Pass, Transaction
from .serializers import PackageSerializer, PassSerializer, TransactionSerializer

MAX_TRIES = 3


class PackageViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

    def get_permissions(self):
        if self.action in ["create", "destroy", "update", "partial_update"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class PassViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Pass.objects.all()
    serializer_class = PassSerializer

    def create(self, request):
        # oh no
        request.data._mutable = True

        package = Package.objects.get(pk=request.data["package"])
        if package.total_time == None:
            return Response(
                {
                    "message": f"Invalid package, {package}. Package must be of prepaid type."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # set code, expiry, and time_left
        request.data["code"] = get_code()
        request.data["time_left"] = package.total_time
        request.data["expires_at"] = timezone.now() + timedelta(
            seconds=package.total_duration
        )

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.validated_data["staff"] = request.user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class TransactionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        package = Package.objects.get(pk=serializer.initial_data["package"])
        if serializer.is_valid(raise_exception=True):
            if package.type == "prepaid":
                if not is_valid_pass(
                    serializer.validated_data["used_pass"],
                    serializer.validated_data["customer"],
                ):
                    return Response(
                        {
                            "message": f"Invalid pass selected, {serializer.validated_data['used_pass']}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def close(self, request, pk=None):
        transaction = self.get_object()
        # if transaction.is_complete:
        #     return Response(
        #         {"message": "Transaction has already been completed."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        transaction.time_out = timezone.now()

        if transaction.package.type == "postpaid":
            transaction.amount = get_amount(
                transaction.time_in, transaction.time_out, transaction.package
            )

        if transaction.package.type == "prepaid":
            print("helo")
            transaction.amount = get_overdue(
                transaction.used_pass,
                transaction.time_in,
                transaction.time_out,
            )

            # update used_pass time left value
            used_pass = Pass.objects.get(id=transaction.used_pass.id)
            used_pass.time_left = get_time_left(
                used_pass.time_left, transaction.time_out, transaction.time_in
            )
            used_pass.save()

        transaction.save()
        return Response(status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]  #
