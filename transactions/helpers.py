import random
import string
from decimal import Decimal

from django.utils import timezone

from transactions.models import Pass

DEFAULT_OVERDUE_RATE = 65


def get_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    code = "".join(random.SystemRandom().choice(alphabet) for _ in range(length))
    while not Pass.objects.filter(code=code, expires_at__gt=timezone.now()).exists():
        return code


def get_amount(time_in, time_out, package):
    total_seconds = (time_out - time_in).total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    total_time = round(hours + (minutes / 60), 2)

    amount = Decimal(str(total_time)) * package.price

    return amount


def get_overdue(used_pass, time_in, time_out):
    """
    updates used_pass by subtracting
    the total seconds consumed from time_left
    """
    used_pass = Pass.objects.get(id=used_pass.id)
    total_seconds = (time_out - time_in).total_seconds()

    time_left = get_time_left(used_pass.time_left, time_out, time_in)

    total_due = 0
    if time_left < 0:
        total_seconds = abs(used_pass.time_left)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        # default premium rate hehe
        total_due = round(hours + (minutes / 60), 2) * DEFAULT_OVERDUE_RATE

    return total_due


def get_available_pass(customer):
    # get passes that have time left and have not yet expired
    qs = customer.customer_passes.get(time_left__gt=0, expires_at__gt=timezone.now())


def get_time_left(initial_time_left, time_out, time_in):
    time_consumed = (time_out - time_in).total_seconds()
    time_left = initial_time_left - time_consumed
    return time_left


def is_valid_pass(used_pass, customer):
    """
    checks if pass still has time left, have not expired
    and whether customer owns the pass
    """
    customer_passes = customer.customer_passes.filter(
        time_left__gt=0, expires_at__gt=timezone.now()
    )

    return bool(used_pass in customer_passes)
