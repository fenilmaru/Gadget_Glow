from celery import shared_task
from datetime import date
from django.db.models import Sum, Count
from django.core.cache import cache
from orders.models import Order
from payments.models import Payment
from products.models import Product
from django.contrib.auth.models import User
from analytics_app.models import DailyAnalytics
import logging

logger = logging.getLogger('gadget_glow')


@shared_task
def generate_daily_analytics():
    today = date.today()
    daily, created = DailyAnalytics.objects.get_or_create(date=today)

    daily.total_orders = Order.objects.filter(created_at__date=today).count()
    daily.total_revenue = Payment.objects.filter(
        status='completed', created_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    daily.new_users = User.objects.filter(date_joined__date=today).count()
    daily.save()

    cache.delete('dashboard_stats')
    cache.delete_pattern('sales_chart_*')

    logger.info(f"Daily analytics generated for {today}")
    return f"Analytics for {today}: {daily.total_orders} orders, ${daily.total_revenue} revenue"
