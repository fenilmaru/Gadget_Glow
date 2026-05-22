from celery import shared_task
from django.contrib.auth.models import User
from notifications.services import create_notification
import logging

logger = logging.getLogger('gadget_glow')


@shared_task
def send_bulk_notification(title, message, notification_type='system', user_ids=None):
    if user_ids:
        users = User.objects.filter(id__in=user_ids)
    else:
        users = User.objects.all()

    count = 0
    for user in users:
        create_notification(user, title, message, notification_type)
        count += 1

    logger.info(f"Sent {count} notifications")
    return count
