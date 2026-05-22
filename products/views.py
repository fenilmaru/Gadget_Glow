from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from products.models import Category, Brand, Product, ProductImage
from products.serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductImageSerializer,
)
from products.services import search_products, get_low_stock_products


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.none()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_featured', 'is_active']
    search_fields = ['name', 'description', 'category__name', 'brand__name']
    ordering_fields = ['price', 'rating', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.action == 'list':
            return Product.objects.filter(is_active=True, is_deleted=False).select_related('category', 'brand')
        return Product.objects.filter(is_deleted=False).select_related('category', 'brand')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        cache_key = 'featured_products'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        products = self.get_queryset().filter(is_featured=True)[:8]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        cache.set(cache_key, serializer.data, 300)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        sort_by = request.query_params.get('sort')
        page = int(request.query_params.get('page', 1))

        if query:
            from ai_features.services import smart_search
            results = smart_search(query)
            serializer = ProductListSerializer(results, many=True, context={'request': request})
            return Response({'results': serializer.data, 'count': len(serializer.data)})

        result = search_products(query, category, None, min_price, max_price, sort_by=sort_by, page=page)
        serializer = ProductListSerializer(result['products'], many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'total': result['total'],
            'page': result['page'],
            'page_size': result['page_size'],
        })

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        products = get_low_stock_products()
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        product = self.get_object()
        related = Product.objects.filter(
            category=product.category, is_active=True, is_deleted=False
        ).exclude(id=product.id)[:4]
        serializer = ProductListSerializer(related, many=True, context={'request': request})
        return Response(serializer.data)


class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs.get('product_pk'))
