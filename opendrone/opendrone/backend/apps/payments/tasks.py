from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_monthly_royalties():
    from .models import RoyaltyLedger
    last_month = (timezone.now().replace(day=1) - timedelta(days=1)).replace(day=1).date()
    unpaid = RoyaltyLedger.objects.filter(is_paid=False, period_month=last_month)
    count = unpaid.update(is_paid=True, paid_at=timezone.now())
    logger.info(f"Elaborate {count} royalty mensili")
    return count
