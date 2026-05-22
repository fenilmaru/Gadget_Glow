from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from users.models import UserProfile
from users.wishlist_models import Wishlist
from users.serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer,
    LoginSerializer, PasswordChangeSerializer, WishlistSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({
            'success': False,
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'success': True, 'message': 'Logged out successfully'})
        except Exception:
            return Response({'success': True, 'message': 'Logged out'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'success': False, 'message': 'Current password is incorrect'},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'success': True, 'message': 'Password changed successfully'})


class WishlistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        items = Wishlist.objects.filter(user=request.user).select_related('product').order_by('-created_at')
        serializer = WishlistSerializer(items, many=True, context={'request': request})
        return Response({'results': serializer.data})

    def create(self, request):
        action_type = request.data.get('action', 'add')
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'success': False, 'message': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)

        if action_type == 'remove':
            deleted, _ = Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
            if deleted:
                return Response({'success': True, 'message': 'Removed from wishlist'})
            return Response({'success': True, 'message': 'Already removed'})
        else:
            from products.models import Product
            try:
                product = Product.objects.get(id=product_id, is_active=True, is_deleted=False)
            except Product.DoesNotExist:
                return Response({'success': False, 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            Wishlist.objects.get_or_create(user=request.user, product=product)
            return Response({'success': True, 'message': 'Added to wishlist'}, status=status.HTTP_201_CREATED)
