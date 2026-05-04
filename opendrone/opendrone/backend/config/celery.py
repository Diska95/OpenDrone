import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('opendrone')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'process-monthly-royalties': {
        'task': 'apps.payments.tasks.process_monthly_royalties',
        'schedule': crontab(day_of_month=1, hour=6, minute=0),
    },
    'update-node-ratings': {
        'task': 'apps.production.tasks.update_node_ratings',
        'schedule': crontab(hour='*/6'),
    },
    'check-sla-compliance': {
        'task': 'apps.orders.tasks.check_sla_compliance',
        'schedule': crontab(minute=0, hour='*/2'),
    },
    'auto-suspend-flagged-projects': {
        'task': 'apps.marketplace.tasks.auto_suspend_flagged_projects',
        'schedule': crontab(minute=0),
    },
}
