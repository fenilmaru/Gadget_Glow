from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from orders.models import Order
from orders.serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
)
from orders.services import place_order
from cart.models import Cart
from payments.services import create_payment
from notifications.services import create_notification


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items__product')
        return Order.objects.filter(user=user).prefetch_related('items__product')

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.items.select_related('product').all()

        for item in cart_items:
            if item.product.available_stock < item.quantity:
                return Response({
                    'error': f'Insufficient stock for {item.product.name}'
                }, status=status.HTTP_400_BAD_REQUEST)

        order, payment = place_order(
            user=request.user,
            cart_items=cart_items,
            shipping_address=serializer.validated_data['shipping_address'],
            payment_method=serializer.validated_data.get('payment_method', 'cod'),
        )

        order_serializer = OrderSerializer(order, context={'request': request})
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ('pending', 'confirmed'):
            return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)

        from orders.services import update_order_status
        if not request.user.is_staff and order.user != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        update_order_status(order.id, 'cancelled')
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from orders.services import update_order_status
        update_order_status(
            order.id,
            serializer.validated_data['status'],
            serializer.validated_data.get('tracking_number', ''),
        )

        order_serializer = OrderSerializer(order, context={'request': request})
        return Response(order_serializer.data)
