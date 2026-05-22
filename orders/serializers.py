from rest_framework import serializers
from orders.models import Order, OrderItem
from products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'total_price', 'shipping_address', 'status',
            'tracking_number', 'notes', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=True)
    payment_method = serializers.ChoiceField(choices=[
        'cod', 'credit_card', 'debit_card', 'paypal', 'upi', 'razorpay', 'stripe'
    ])
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    def validate_shipping_address(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a complete shipping address")
        return value


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        'confirmed', 'packed', 'shipped', 'delivered', 'cancelled', 'returned'
    ])
    tracking_number = serializers.CharField(required=False, allow_blank=True)
