from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_order_confirmation(order):
    try:
        send_mail(
            subject=f'OpenDrone — Ordine #{order.id} confermato',
            message=f'Il tuo ordine per "{order.project.title}" è stato confermato. Totale: €{order.total_amount}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Errore invio email ordine {order.id}: {e}")


def send_order_shipped(order):
    try:
        tracking_info = f'\nTracking: {order.tracking_number}' if order.tracking_number else ''
        send_mail(
            subject=f'OpenDrone — Ordine #{order.id} spedito',
            message=f'Il tuo ordine per "{order.project.title}" è stato spedito.{tracking_info}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Errore invio email spedizione {order.id}: {e}")
