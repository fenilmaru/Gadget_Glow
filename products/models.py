from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from Gadget_Glow.utils import generate_slug


class Category(models.Model):
    CATEGORY_IMAGES = {
        'mobile cases': 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400&h=400&fit=crop',
        'chargers': 'https://images.unsplash.com/photo-1617791160536-598cf32026fb?w=400&h=400&fit=crop',
        'chargers': 'https://images.unsplash.com/photo-1617791160536-598cf32026fb?w=400&h=400&fit=crop',
        'cables': 'https://images.unsplash.com/photo-1544731612-de7f96afe55f?w=400&h=400&fit=crop',
        'power banks': 'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?w=400&h=400&fit=crop',
        'smart watches': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
        'phone holders': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=400&h=400&fit=crop',
        'default': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop',
    }

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name)
        super().save(*args, **kwargs)

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url') and self.image.name:
            try:
                return self.image.url
            except (ValueError, AttributeError):
                pass
        name_lower = self.name.lower()
        for key, url in self.CATEGORY_IMAGES.items():
            if key in name_lower or name_lower in key:
                return url
        return 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop'

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name)
        super().save(*args, **kwargs)

    def get_logo_url(self):
        if self.logo and hasattr(self.logo, 'url') and self.logo.name:
            try:
                return self.logo.url
            except (ValueError, AttributeError):
                pass
        slug_map = {
            'anker': 'anker', 'apple': 'apple', 'boat': 'boat', 'jbl': 'jbl',
            'noise': 'noise', 'oneplus': 'oneplus', 'realme': 'realme',
            'samsung': 'samsung', 'sony': 'sony', 'xiaomi': 'xiaomi',
        }
        slug_lower = self.slug.lower() if self.slug else ''
        for key, name in slug_map.items():
            if key in slug_lower:
                return f'/static/images/brands/{name}.png'
        return None

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['stock']),
            models.Index(fields=['-rating']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name)
        super().save(*args, **kwargs)

    @property
    def available_stock(self):
        return self.stock - self.reserved_stock

    @property
    def in_stock(self):
        return self.available_stock > 0

    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

    UNSPLASH_IMAGES = {
        'chargers': {
            'fast charger': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop',
            'wireless charger': 'https://images.unsplash.com/photo-1623869675781-80aa31012a5a?w=400&h=400&fit=crop',
            'type-c charger': 'https://images.unsplash.com/photo-1617791160536-598cf32026fb?w=400&h=400&fit=crop',
            'power adapter': 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=400&h=400&fit=crop',
            'car charger': 'https://images.unsplash.com/photo-1619767886558-efdc7b9af1ca?w=400&h=400&fit=crop',
            'default': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop',
        },
        'power banks': {
            'slim': 'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?w=400&h=400&fit=crop',
            'fast charging': 'https://images.unsplash.com/photo-1609592425209-5c0b89d642ae?w=400&h=400&fit=crop',
            'magsafe': 'https://images.unsplash.com/photo-1625052002415-30350d35b34f?w=400&h=400&fit=crop',
            'default': 'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?w=400&h=400&fit=crop',
        },
        'smart watches': {
            'fitness': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
            'amoled': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&h=400&fit=crop',
            'sports': 'https://images.unsplash.com/photo-1546868871-af0de0ae72cb?w=400&h=400&fit=crop',
            'default': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
        },
        'mobile cases': {
            'transparent': 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400&h=400&fit=crop',
            'silicon': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=400&h=400&fit=crop',
            'gaming case': 'https://images.unsplash.com/photo-1606041008023-472dfb5e530a?w=400&h=400&fit=crop',
            'leather': 'https://images.unsplash.com/photo-1557330353-ff1e9d5c1b5e?w=400&h=400&fit=crop',
            'default': 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400&h=400&fit=crop',
        },
        'phone holders': {
            'holder': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=400&h=400&fit=crop',
            'stand': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=400&h=400&fit=crop',
            'mount': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=400&h=400&fit=crop',
            'default': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=400&h=400&fit=crop',
        },
        'cables': {
            'usb cable': 'https://images.unsplash.com/photo-1544731612-de7f96afe55f?w=400&h=400&fit=crop',
            'lightning': 'https://images.unsplash.com/photo-1617791160536-598cf32026fb?w=400&h=400&fit=crop',
            'type-c': 'https://images.unsplash.com/photo-1544731612-de7f96afe55f?w=400&h=400&fit=crop',
            'default': 'https://images.unsplash.com/photo-1544731612-de7f96afe55f?w=400&h=400&fit=crop',
        },
        'accessories': {
            'default': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop',
        },
        'default': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop',
    }

    CATEGORY_BANNERS = {
        'chargers': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=1200&h=600&fit=crop',
        'power banks': 'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?w=1200&h=600&fit=crop',
        'smart watches': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1200&h=600&fit=crop',
        'mobile cases': 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=1200&h=600&fit=crop',
        'cables': 'https://images.unsplash.com/photo-1544731612-de7f96afe55f?w=1200&h=600&fit=crop',
        'default': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=1200&h=600&fit=crop',
    }

    def get_display_image(self):
        if self.image and hasattr(self.image, 'url') and self.image.name:
            try:
                return self.image.url
            except (ValueError, AttributeError):
                pass
        return self.get_unsplash_url()

    def get_unsplash_url(self):
        name_lower = self.name.lower()
        cat_lower = self.category.name.lower() if self.category else ''

        cat_map = {
            'charger': 'chargers', 'adapter': 'chargers',
            'power bank': 'power banks', 'powerbank': 'power banks',
            'watch': 'smart watches', 'band': 'smart watches',
            'case': 'mobile cases', 'cover': 'mobile cases', 'armor': 'mobile cases',
            'cable': 'cables', 'lightning': 'cables', 'usb': 'cables',
            'holder': 'phone holders', 'stand': 'phone holders', 'mount': 'phone holders',
        }

        image_group = 'default'
        for key, group in cat_map.items():
            if key in name_lower or key in cat_lower:
                image_group = group
                break

        raw = self.UNSPLASH_IMAGES.get(image_group, self.UNSPLASH_IMAGES['default'])

        # 'default' group is a plain URL string, others are dicts of keyword -> URL
        if isinstance(raw, str):
            return raw

        for key, url in raw.items():
            if key != 'default' and key in name_lower:
                return url

        return raw.get('default', self.UNSPLASH_IMAGES['default'])

    @classmethod
    def get_category_banner(cls, category_name):
        if not category_name:
            return cls.CATEGORY_BANNERS['default']
        cat_lower = category_name.lower()
        for key, url in cls.CATEGORY_BANNERS.items():
            if key in cat_lower:
                return url
        return cls.CATEGORY_BANNERS['default']

    def update_rating(self):
        avg = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        self.rating = round(avg or 0, 2)
        self.total_reviews = self.reviews.count()
        self.save(update_fields=['rating', 'total_reviews'])

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"
