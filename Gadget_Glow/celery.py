import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gadget_Glow.settings')

app = Celery('Gadget_Glow')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
