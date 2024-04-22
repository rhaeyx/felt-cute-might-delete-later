from django.db import models
from django.utils import timezone

from customers.models import Customer
from users.models import User


class Package(models.Model):
    TYPES = [("prepaid", "Prepaid"), ("postpaid", "Postpaid")]

    name = models.CharField("Name", max_length=100)
    type = models.CharField("Type", max_length=9, choices=TYPES)
    description = models.TextField("Description")
    price = models.DecimalField("Price", max_digits=7, decimal_places=2)
    total_time = models.IntegerField("Total Time", null=True)
    total_duration = models.IntegerField("Expiry Duration", null=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)

    def __str__(self):
        return self.name


class Pass(models.Model):
    code = models.CharField("Code", max_length=8, unique=True)
    time_left = models.IntegerField("Time Left (Seconds)")
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    expires_at = models.DateTimeField("Expires At")
    updated_at = models.DateTimeField("Updated At", auto_now=True)

    package = models.ForeignKey(
        Package,
        on_delete=models.DO_NOTHING,
        verbose_name="Package",
        limit_choices_to={"type": "prepaid"},
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.DO_NOTHING,
        verbose_name="Customer",
        related_name="customer_passes",
    )
    staff = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Staff")

    def __str__(self):
        return self.code


class Transaction(models.Model):
    PAYMENT_METHODS = [
        ("GCash", "Paid with GCash"),
        ("Cash", "Paid with cash"),
        ("Other", "Other payment method"),
    ]

    time_in = models.DateTimeField("Time In", auto_now_add=True)
    time_out = models.DateTimeField("Time Out", null=True)
    amount = models.IntegerField("Total Amount", null=True)
    payment_method = models.CharField(
        "Payment Method", max_length=20, choices=PAYMENT_METHODS
    )

    package = models.ForeignKey(
        Package, on_delete=models.DO_NOTHING, verbose_name="Package"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.DO_NOTHING, verbose_name="Customer"
    )
    staff = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Staff")
    used_pass = models.ForeignKey(
        Pass, on_delete=models.DO_NOTHING, verbose_name="Used Pass", null=True
    )

    created_at = models.DateTimeField("Created At", auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)

    @property
    def is_complete(self):
        return bool(self.time_out != None)

    @property
    def time_consumed(self):
        if self.time_out != None:
            return str(self.time_out - self.time_in)
        return str(timezone.now() - self.time_in)
