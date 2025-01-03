from django.utils import timezone

from dateutil.relativedelta import relativedelta

from celery import shared_task

from business.models import Business, Transaction


@shared_task
def check_expiring_tariffs():
    today = timezone.localtime(timezone.now()).date()
    expiring_date = today + relativedelta(days=3)
    businesses = Business.objects.filter(tariff_end_day=expiring_date)
    for business in businesses:
        if business.tariff.price != 0:
            business.create_tariff_expiring_notification()


@shared_task
def update_tariffs():
    today = timezone.localtime(timezone.now()).date()
    businesses = Business.objects.filter(tariff_end_day=today)
    for business in businesses:
        tariff = business.tariff
        transaction = Transaction(
            business=business, amount=tariff.price,
            type_of_transaction=Transaction.WITHDRAWAL,
            description=Transaction.get_tariff_description(tariff)
        )
        try:
            business = Business.decrease_balance(business.pk, tariff.price)
            business.set_tariff_end_day()
            transaction.success = True
            transaction.save()
        except ValueError:
            business.set_standard_tariff()
            transaction.success = False
            transaction.save()
        business.create_tariff_update_notification()
