from celery import shared_task
import logging
from .models import DroneProject

logger = logging.getLogger(__name__)


@shared_task
def auto_suspend_flagged_projects():
    threshold = 5
    flagged = DroneProject.objects.filter(
        flag_count__gte=threshold,
        status=DroneProject.Status.PUBLISHED
    )
    count = flagged.update(status=DroneProject.Status.SUSPENDED)
    if count:
        logger.info(f"Sospesi {count} progetti per troppe segnalazioni")
    return count
