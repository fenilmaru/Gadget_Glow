from rest_framework import serializers
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'min_order_amount', 'max_discount_amount', 'valid_from', 'valid_to',
            'usage_limit', 'used_count', 'is_active', 'is_valid', 'created_at'
        ]

class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
