from django.db import models


class Customer(models.Model):
    first_name = models.CharField("First Name", max_length=100)
    last_name = models.CharField("Last Name", max_length=100)
    phone_number = models.CharField("Phone Number", max_length=11)
    email = models.EmailField()
    created_at = models.DateTimeField("Join Date", auto_now_add=True)
    updated_at = models.DateTimeField("Last Updated", auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def join_date(self):
        date = self.created_at.strftime("%B %d, %G")
        return date

    # todo: last active, based on last transaction
