from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from users.views import WishlistViewSet

from .views import (
    home, user_login, user_register, user_logout, products_page, product_detail,
    orders_page, admin_dashboard, cart_page, wishlist_page, profile_page,
    checkout_page, notifications_page, ai_chatbot_page,
    admin_categories, admin_category_add, admin_category_edit, admin_category_delete,
    admin_products, admin_product_add, admin_product_edit, admin_product_delete,
    admin_product_toggle_featured, admin_product_toggle_active,
    admin_product_bulk_delete, admin_category_bulk_delete,
)

schema_view = get_schema_view(
    openapi.Info(
        title='Gadget Glow API',
        default_version='v1',
        description='AI-Powered E-Commerce API for Mobile Accessories',
        terms_of_service='https://gadgetglow.com/terms/',
        contact=openapi.Contact(email='api@gadgetglow.com'),
        license=openapi.License(name='MIT License'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('products/', products_page, name='products_page'),
    path('products/<slug:slug>/', product_detail, name='product_detail'),
    path('orders/', orders_page, name='orders_page'),
    path('cart/', cart_page, name='cart_page'),
    path('wishlist/', wishlist_page, name='wishlist_page'),
    path('profile/', profile_page, name='profile_page'),
    path('checkout/', checkout_page, name='checkout_page'),
    path('notifications/', notifications_page, name='notifications_page'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/categories/', admin_categories, name='admin_categories'),
    path('dashboard/categories/add/', admin_category_add, name='admin_category_add'),
    path('dashboard/categories/<int:cat_id>/edit/', admin_category_edit, name='admin_category_edit'),
    path('dashboard/categories/<int:cat_id>/delete/', admin_category_delete, name='admin_category_delete'),
    path('dashboard/products/', admin_products, name='admin_products'),
    path('dashboard/products/add/', admin_product_add, name='admin_product_add'),
    path('dashboard/products/<int:prod_id>/edit/', admin_product_edit, name='admin_product_edit'),
    path('dashboard/products/<int:prod_id>/delete/', admin_product_delete, name='admin_product_delete'),
    path('dashboard/products/<int:prod_id>/toggle-featured/', admin_product_toggle_featured, name='admin_product_toggle_featured'),
    path('dashboard/products/<int:prod_id>/toggle-active/', admin_product_toggle_active, name='admin_product_toggle_active'),
    path('dashboard/products/bulk-delete/', admin_product_bulk_delete, name='admin_product_bulk_delete'),
    path('dashboard/categories/bulk-delete/', admin_category_bulk_delete, name='admin_category_bulk_delete'),
    path('ai-chatbot/', ai_chatbot_page, name='ai_chatbot_page'),

    # API v1
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/wishlist/', WishlistViewSet.as_view({'get': 'list', 'post': 'create'}), name='wishlist-api'),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/cart/', include('cart.urls')),
    path('api/v1/orders/', include('orders.urls')),
    path('api/v1/payments/', include('payments.urls')),
    path('api/v1/reviews/', include('reviews.urls')),
    path('api/v1/ai/', include('ai_features.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/analytics/', include('analytics_app.urls')),
    path('api/v1/coupons/', include('discounts.urls')),

    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
