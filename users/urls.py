from django.urls import path
from users.views import RegisterView, LoginView, LogoutView, UserProfileView, ChangePasswordView, WishlistViewSet
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('profile/', UserProfileView.as_view(), name='auth-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token-blacklist'),
    path('wishlist/', WishlistViewSet.as_view({'get': 'list', 'post': 'create', 'delete': 'destroy'}), name='wishlist-api'),
]
