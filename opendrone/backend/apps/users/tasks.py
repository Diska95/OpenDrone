"""Task Celery per manutenzione utenti / JWT."""
import logging
from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger(__name__)


@shared_task(name='apps.users.tasks.flush_expired_jwt')
def flush_expired_jwt():
    """Rimuove i refresh token scaduti dalla tabella outstanding_token.

    Schedulato giornalmente via django_celery_beat (vedi management command
    `setup_periodic_tasks`). Senza questo job la tabella cresce all'infinito.
    """
    call_command('flushexpiredtokens')
    logger.info('flush_expired_jwt: completato')
    return 'OK'
