from django.conf import settings

DAY = 'DAY'
MONTH = 'MONTH'
YEAR = 'YEAR'

DURATION_CHOICES = (
    (DAY, 'DAY'),
    (MONTH, 'MONTH'),
    (YEAR, 'YEAR'),
)

#用户拖欠费用阈值
USER_ARREARS_THEESHOLD = getattr(settings, 'USER_ARREARS_THEESHOLD', 0.0)
#用户可以多次约课的阈值
MAKE_RECURRING_APPOINTMENT_THEESHOLD = getattr(settings, 'MAKE_RECURRING_APPOINTMENT_THEESHOLD', 5.0)
USER_ARREARS_PUSH_THEESHOLD = getattr(settings, 'USER_ARREARS_PUSH_THEESHOLD', 3)


START_ID = 1000000000000000

END_ID = 9000000000000000


CURRENCY_CHOICES = {
    'AUD': 'Australian Dollar',
    'CAD': 'Canadian Dollar',
    'EUR': 'Euro',
    'HKD': 'Hong Kong Dollar',
    'JPY': 'Japanese Yen',
    'NZD': 'New Zealand Dollar',
    'GBP': 'Pound Sterling',
    'SGD': 'Singapore Dollar',
    'USD': 'U.S. Dollar'
}
