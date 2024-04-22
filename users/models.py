from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Meta:
        db_table = "auth_user"

    # Base Class: First Name, Last Name, Email, Username, Password
    phone_number = models.CharField("Contact Number", max_length=11)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
