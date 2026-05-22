from django.contrib import admin
from analytics_app.models import AuditLog, DailyAnalytics


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'model_name']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'details', 'ip_address', 'created_at']


@admin.register(DailyAnalytics)
class DailyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_visitors', 'total_orders', 'total_revenue', 'new_users']
    list_filter = ['date']
    readonly_fields = ['date', 'total_visitors', 'total_orders', 'total_revenue', 'total_products_sold', 'new_users']
