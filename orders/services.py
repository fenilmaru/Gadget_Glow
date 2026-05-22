import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from django.db.models import F
from django.core.cache import cache
from orders.models import Order, OrderItem
from products.models import Product
from notifications.services import create_notification
from payments.services import create_payment

logger = logging.getLogger('gadget_glow')


@transaction.atomic
def place_order(user, cart_items, shipping_address, payment_method, coupon_discount=0):
    total = sum(item.subtotal for item in cart_items)
    total_after_discount = total - coupon_discount

    order = Order.objects.create(
        user=user,
        total_price=total_after_discount,
        shipping_address=shipping_address,
        status='pending'
    )

    for cart_item in cart_items:
        product = cart_item.product
        if product.available_stock < cart_item.quantity:
            raise ValueError(f"Insufficient stock for {product.name}")

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=cart_item.quantity,
            price=cart_item.price * cart_item.quantity
        )

        Product.objects.filter(id=product.id).update(
            stock=F('stock') - cart_item.quantity
        )

    payment = create_payment(order, total_after_discount, payment_method)

    create_notification(
        user=user,
        title='Order Placed',
        message=f'Your order #{order.id} has been placed successfully!',
        notification_type='order',
        link=f'/orders/{order.id}/'
    )

    cart_items.delete()
    cache.delete(f'cart_{user.id}')

    return order, payment


@transaction.atomic
def update_order_status(order_id, new_status, tracking_number=None):
    order = Order.objects.get(id=order_id)
    order.status = new_status
    if tracking_number:
        order.tracking_number = tracking_number
    order.save()

    _send_order_status_ws(order, new_status, tracking_number)

    create_notification(
        user=order.user,
        title=f'Order {new_status.title()}',
        message=f'Your order #{order.id} has been {new_status}.',
        notification_type='order' if new_status in ('shipped', 'delivered') else 'shipping',
        link=f'/orders/{order.id}/'
    )

    return order


def _send_order_status_ws(order, new_status, tracking_number):
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'order_{order.id}',
                {
                    'type': 'order_status_update',
                    'order_id': order.id,
                    'status': new_status,
                    'tracking_number': tracking_number or '',
                }
            )
    except Exception as e:
        logger.warning(f"WebSocket order status send failed: {e}")


def get_user_orders(user):
    cache_key = f'user_orders_{user.id}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    orders = Order.objects.filter(user=user).prefetch_related('items__product').order_by('-created_at')
    cache.set(cache_key, list(orders), 300)
    return orders
