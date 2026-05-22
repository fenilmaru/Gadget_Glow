import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from notifications.models import Notification

logger = logging.getLogger('gadget_glow')


def create_notification(user, title, message, notification_type='system', link=''):
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )
    _send_notification_ws(notification)
    return notification


def _send_notification_ws(notification):
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'notifications_{notification.user_id}',
                {
                    'type': 'new_notification',
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'link': notification.link,
                }
            )
    except Exception as e:
        logger.warning(f"WebSocket send failed: {e}")


def _send_unread_count_ws(user_id, count):
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user_id}',
                {
                    'type': 'unread_count',
                    'count': count,
                }
            )
    except Exception as e:
        logger.warning(f"WebSocket send unread count failed: {e}")


def get_unread_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()


def mark_as_read(notification_id, user):
    Notification.objects.filter(id=notification_id, user=user).update(is_read=True)
    count = get_unread_count(user)
    _send_unread_count_ws(user.id, count)


def mark_all_as_read(user):
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    _send_unread_count_ws(user.id, 0)


def delete_notification(notification_id, user):
    Notification.objects.filter(id=notification_id, user=user).delete()
    count = get_unread_count(user)
    _send_unread_count_ws(user.id, count)
