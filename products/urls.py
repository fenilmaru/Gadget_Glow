from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import CategoryViewSet, BrandViewSet, ProductViewSet, ProductImageViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('brands', BrandViewSet)
router.register('', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
