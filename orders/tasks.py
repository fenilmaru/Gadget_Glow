from celery import shared_task
from orders.models import Order
from orders.services import update_order_status
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('gadget_glow')


@shared_task
def auto_confirm_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.status == 'pending':
            update_order_status(order_id, 'confirmed')
            logger.info(f"Order {order_id} auto-confirmed")
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")


@shared_task
def cleanup_expired_orders(days=7):
    cutoff = datetime.now() - timedelta(days=days)
    expired = Order.objects.filter(
        status='pending',
        created_at__lte=cutoff
    )
    count = expired.count()
    expired.update(status='cancelled')
    logger.info(f"Cancelled {count} expired orders")
    return count
