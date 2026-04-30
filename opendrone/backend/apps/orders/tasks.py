from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_sla_compliance():
    from .models import Order
    threshold = timezone.now() - timedelta(hours=96)
    late_orders = Order.objects.filter(
        status=Order.Status.ASSIGNED_PRINT,
        payment_confirmed_at__lt=threshold
    )
    for order in late_orders:
        logger.warning(f"Ordine #{order.id} in ritardo SLA — nodo: {order.print_node}")
    return late_orders.count()
