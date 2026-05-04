from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_node_ratings():
    from apps.users.models import PrintNodeProfile
    from apps.orders.models import Order

    for node_profile in PrintNodeProfile.objects.filter(is_active=True):
        orders = Order.objects.filter(print_node=node_profile.user, status=Order.Status.DELIVERED)
        count = orders.count()
        if count > 0:
            node_profile.total_orders_completed = count
            node_profile.save(update_fields=['total_orders_completed'])
    return True
