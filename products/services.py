import logging
from django.db import transaction
from django.db.models import Q, Count
from django.core.cache import cache
from products.models import Product, Category, Brand

logger = logging.getLogger('gadget_glow')


def search_products(query, category=None, brand=None, min_price=None, max_price=None,
                    in_stock=None, sort_by=None, page=1, page_size=20):
    cache_key = f"search:{query}:{category}:{brand}:{min_price}:{max_price}:{in_stock}:{sort_by}:{page}:{page_size}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = Product.objects.select_related('category', 'brand').filter(is_active=True, is_deleted=False)

    if query:
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        )

    if category:
        qs = qs.filter(category_id=category)
    if brand:
        qs = qs.filter(brand_id=brand)
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)
    if in_stock:
        qs = qs.filter(stock__gt=0)

    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        'rating': '-rating',
        'newest': '-created_at',
        'name': 'name',
        'popular': '-total_reviews',
    }
    if sort_by in sort_map:
        qs = qs.order_by(sort_map[sort_by])

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    results = list(qs[start:end])

    result = {'products': results, 'total': total, 'page': page, 'page_size': page_size}
    cache.set(cache_key, result, 300)
    return result


def get_low_stock_products(threshold=5):
    return Product.objects.filter(is_active=True, is_deleted=False, stock__lte=threshold)


def get_top_selling_products(limit=10):
    cache_key = 'top_selling_products'
    cached = cache.get(cache_key)
    if cached:
        return cached
    from orders.models import OrderItem
    products = Product.objects.filter(
        is_active=True, is_deleted=False
    ).annotate(
        total_sold=Count('orderitem')
    ).order_by('-total_sold')[:limit]
    cache.set(cache_key, list(products), 3600)
    return products
