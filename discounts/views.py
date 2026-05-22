from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Coupon
from .serializers import CouponSerializer, CouponApplySerializer

class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Coupon.objects.filter(is_active=True)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def apply(self, request):
        serializer = CouponApplySerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            try:
                coupon = Coupon.objects.get(code=code, is_active=True)
                if coupon.is_valid:
                    return Response({
                        'valid': True,
                        'code': coupon.code,
                        'discount_type': coupon.discount_type,
                        'discount_value': coupon.discount_value,
                        'max_discount_amount': coupon.max_discount_amount,
                        'message': f'Coupon applied! You get {coupon.discount_value}{"%" if coupon.discount_type == "percentage" else " off"}'
                    })
                return Response({'valid': False, 'message': 'Coupon is expired or fully used'}, status=400)
            except Coupon.DoesNotExist:
                return Response({'valid': False, 'message': 'Invalid coupon code'}, status=400)
        return Response(serializer.errors, status=400)
