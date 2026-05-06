"""Crea/aggiorna i PeriodicTask di django_celery_beat usati dall'app.

Idempotente: si puo' lanciare piu' volte senza effetti collaterali.

Uso:
    docker compose -f opendrone/docker-compose.prod.yml exec backend \
        python manage.py setup_periodic_tasks
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Registra i PeriodicTask Celery beat (cleanup JWT, retention, ecc.)'

    def handle(self, *args, **options):
        self.stdout.write('Setup PeriodicTask in corso...')

        # ─── Schedule ogni 24 ore ──────────────────────────────────
        daily_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,
        )

        # ─── Task: flush JWT scaduti (giornaliero) ─────────────────
        task, created = PeriodicTask.objects.update_or_create(
            name='Flush expired JWT tokens',
            defaults={
                'interval': daily_schedule,
                'task': 'apps.users.tasks.flush_expired_jwt',
                'enabled': True,
                'description': (
                    'Rimuove dalla tabella outstanding_token i refresh JWT gia\' scaduti. '
                    'Senza questo la tabella cresce all\'infinito.'
                ),
            }
        )
        action = 'creato' if created else 'aggiornato'
        self.stdout.write(self.style.SUCCESS(f'  ✓ {task.name}: {action}'))

        self.stdout.write(self.style.SUCCESS('Done.'))
