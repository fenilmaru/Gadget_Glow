from rest_framework import serializers
from products.models import Category, Brand, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'image_url', 'is_active', 'product_count', 'created_at']

    def get_image_url(self, obj):
        return obj.get_image_url()

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True, is_deleted=False).count()


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'is_active', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'alt_text', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    brand = serializers.StringRelatedField(read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    display_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'compare_price', 'discount_percentage',
            'image', 'display_image', 'category', 'brand', 'stock', 'in_stock',
            'rating', 'total_reviews', 'is_featured', 'created_at',
        ]

    def get_display_image(self, obj):
        return obj.get_display_image()


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    available_stock = serializers.ReadOnlyField()
    display_image = serializers.SerializerMethodField()

    def get_display_image(self, obj):
        return obj.get_display_image()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'compare_price',
            'discount_percentage', 'image', 'display_image', 'images', 'category', 'brand',
            'seller', 'stock', 'available_stock', 'in_stock', 'reserved_stock',
            'rating', 'total_reviews', 'is_featured', 'is_active',
            'created_at', 'updated_at',
        ]
