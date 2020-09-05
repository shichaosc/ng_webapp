from common.models import ExchangeRate
from django.utils import timezone


def get_currency_id():

    now_time = timezone.now()
    exchange_rate = ExchangeRate.objects.filter(valid_start__lte=now_time, valid_end__gt=now_time).all()

    rate_id = []

    for rate in exchange_rate:

        rate_id.append((rate.id, rate.currency))

    return tuple(rate_id)


def get_currency():

    now_time = timezone.now()
    exchange_rate = ExchangeRate.objects.filter(recharge=ExchangeRate.DISPLAY, valid_start__lte=now_time, valid_end__gt=now_time).all()

    rate_currency = []

    for rate in exchange_rate:

        rate_currency.append((rate.currency, rate.currency))

    return tuple(rate_currency)


def get_currency_rate():

    now_time = timezone.now()
    exchange_rate = ExchangeRate.objects.filter(valid_start__lte=now_time, valid_end__gt=now_time).all()

    rate_list = []

    for rate in exchange_rate:

        rate_list.append((rate.rate, rate.currency))

    return tuple(rate_list)
