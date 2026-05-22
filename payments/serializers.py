from rest_framework import serializers
from payments.models import Payment, TransactionLog


class TransactionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLog
        fields = ['id', 'action', 'status', 'details', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    logs = TransactionLogSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'user', 'amount', 'method', 'status',
            'transaction_id', 'gateway_response', 'logs', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'transaction_id', 'status', 'created_at', 'updated_at']


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    method = serializers.ChoiceField(choices=[
        'credit_card', 'debit_card', 'paypal', 'upi', 'cod', 'razorpay', 'stripe'
    ])

    def validate_order_id(self, value):
        from orders.models import Order
        if not Order.objects.filter(id=value).exists():
            raise serializers.ValidationError("Order not found")
        return value
