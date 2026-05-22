from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from notifications.models import Notification


@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            title='Order Placed',
            message=f'Your order #{instance.id} has been placed successfully!',
            notification_type='order',
            link=f'/orders/{instance.id}/',
        )
    elif instance.status in ('shipped', 'delivered', 'cancelled'):
        emoji = {'shipped': 'shipped', 'delivered': 'delivered', 'cancelled': 'cancelled'}
        Notification.objects.create(
            user=instance.user,
            title=f'Order {instance.status.title()}',
            message=f'Your order #{instance.id} has been {instance.status}.',
            notification_type='order' if instance.status in ('shipped', 'delivered') else 'shipping',
            link=f'/orders/{instance.id}/',
        )
