from django.contrib import admin
from products.models import Category, Brand, Product, ProductImage
from reviews.models import Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['user', 'rating', 'comment']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'stock', 'available_stock', 'rating', 'is_featured', 'is_active']
    list_filter = ['category', 'brand', 'is_featured', 'is_active', 'is_deleted']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    readonly_fields = ['rating', 'total_reviews', 'available_stock']
    fieldsets = [
        ('Basic Info', {'fields': ['name', 'slug', 'description', 'image']}),
        ('Pricing', {'fields': ['price', 'compare_price']}),
        ('Categories', {'fields': ['category', 'brand', 'seller']}),
        ('Inventory', {'fields': ['stock', 'reserved_stock', 'available_stock']}),
        ('Status', {'fields': ['is_featured', 'is_active', 'is_deleted']}),
        ('Ratings', {'fields': ['rating', 'total_reviews']}),
    ]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'created_at']
    list_filter = ['is_primary']
