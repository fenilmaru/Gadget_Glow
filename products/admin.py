from django.contrib import admin
from django.utils.html import format_html
from products.models import Category, Brand, Product, ProductImage
from reviews.models import Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;" />', obj.image.url)
        return ''
    image_preview.short_description = 'Preview'


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['user', 'rating', 'comment']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'name', 'slug', 'is_active', 'product_count', 'created_at']
    list_display_links = ['name']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['is_active']
    readonly_fields = ['image_preview']

    def image_tag(self, obj):
        url = obj.get_image_url()
        if url:
            return format_html('<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:50%;" />', url)
        return ''
    image_tag.short_description = 'Image'

    def image_preview(self, obj):
        url = obj.get_image_url()
        if url:
            return format_html('<img src="{}" style="width:200px;height:200px;object-fit:cover;border-radius:12px;" />', url)
        return ''
    image_preview.short_description = 'Preview'

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'name', 'category', 'price', 'stock', 'rating', 'is_featured', 'is_active']
    list_display_links = ['name']
    list_filter = ['category', 'brand', 'is_featured', 'is_active', 'is_deleted']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    readonly_fields = ['image_preview', 'rating', 'total_reviews', 'available_stock']
    fieldsets = [
        ('Basic Info', {'fields': ['name', 'slug', 'description', 'image', 'image_preview']}),
        ('Pricing', {'fields': ['price', 'compare_price']}),
        ('Categories', {'fields': ['category', 'brand', 'seller']}),
        ('Inventory', {'fields': ['stock', 'reserved_stock', 'available_stock']}),
        ('Status', {'fields': ['is_featured', 'is_active', 'is_deleted']}),
        ('Ratings', {'fields': ['rating', 'total_reviews']}),
    ]

    def image_tag(self, obj):
        url = obj.get_display_image()
        if url:
            return format_html('<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:8px;" />', url)
        return ''
    image_tag.short_description = 'Image'

    def image_preview(self, obj):
        url = obj.get_display_image()
        if url:
            return format_html('<img src="{}" style="width:200px;height:200px;object-fit:cover;border-radius:12px;" />', url)
        return ''
    image_preview.short_description = 'Preview'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'product', 'is_primary', 'created_at']
    list_filter = ['is_primary']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;" />', obj.image.url)
        return ''
    image_preview.short_description = 'Preview'
