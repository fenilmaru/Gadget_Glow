import logging
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.core.cache import cache
from orders.models import Order
from payments.models import Payment
from products.models import Product
from django.contrib.auth.models import User

logger = logging.getLogger('gadget_glow')


def get_dashboard_stats():
    cache_key = 'dashboard_stats'
    cached = cache.get(cache_key)
    if cached:
        return cached

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    stats = {
        'total_products': Product.objects.filter(is_deleted=False).count(),
        'total_orders': Order.objects.count(),
        'total_users': User.objects.filter(is_staff=False).count(),
        'total_revenue': Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'pending_orders': Order.objects.filter(status='pending').count(),
        'low_stock_products': Product.objects.filter(is_active=True, is_deleted=False, stock__lte=5).count(),
        'weekly_orders': Order.objects.filter(created_at__gte=week_ago).count(),
        'weekly_revenue': Payment.objects.filter(status='completed', created_at__gte=week_ago).aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'monthly_orders': Order.objects.filter(created_at__gte=month_ago).count(),
        'monthly_revenue': Payment.objects.filter(status='completed', created_at__gte=month_ago).aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'new_users_month': User.objects.filter(is_staff=False, date_joined__gte=month_ago).count(),
    }

    cache.set(cache_key, stats, 300)
    return stats


def get_sales_chart_data(days=30):
    cache_key = f'sales_chart_{days}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    start_date = datetime.now().date() - timedelta(days=days)
    orders = Order.objects.filter(created_at__gte=start_date)
    payments = Payment.objects.filter(status='completed', created_at__gte=start_date)

    data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        day_orders = orders.filter(created_at__date=date).count()
        day_revenue = payments.filter(created_at__date=date).aggregate(
            total=Sum('amount')
        )['total'] or 0
        data.append({
            'date': date.isoformat(),
            'orders': day_orders,
            'revenue': float(day_revenue),
        })

    cache.set(cache_key, data, 3600)
    return data


def get_top_products(limit=10):
    from orders.models import OrderItem
    products = Product.objects.filter(
        is_deleted=False
    ).annotate(
        total_sold=Sum('orderitem__quantity'),
        total_revenue=Sum('orderitem__price'),
    ).order_by('-total_sold')[:limit]

    return [
        {
            'id': p.id,
            'name': p.name,
            'total_sold': p.total_sold or 0,
            'total_revenue': float(p.total_revenue or 0),
            'stock': p.stock,
        }
        for p in products
    ]
