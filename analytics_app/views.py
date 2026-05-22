from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from analytics_app.models import AuditLog
from analytics_app.serializers import AuditLogSerializer
from analytics_app.services import get_dashboard_stats, get_sales_chart_data, get_top_products


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        stats = get_dashboard_stats()
        return Response(stats)

    @action(detail=False, methods=['get'])
    def sales_chart(self, request):
        days = int(request.query_params.get('days', 30))
        data = get_sales_chart_data(days)
        return Response(data)

    @action(detail=False, methods=['get'])
    def top_products(self, request):
        products = get_top_products()
        return Response(products)

    @action(detail=False, methods=['get'])
    def audit_logs(self, request):
        logs = AuditLog.objects.all()[:100]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
