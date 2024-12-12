import datetime

from django.core.exceptions import ValidationError


def validate_age(value: datetime.date):
    if value > datetime.date.today() - datetime.timedelta(days=365 * 18):
        raise ValidationError("You must be at least 18 years old")
