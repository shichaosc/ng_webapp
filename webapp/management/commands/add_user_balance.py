from django.core.management.base import BaseCommand
from finance.models import RechargeOrder


class Command(BaseCommand):

    def handle(self, *args, **options):

        RechargeOrder.objects.filter()