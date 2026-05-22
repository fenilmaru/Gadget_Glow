import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from products.models import Product
from reviews.models import Review

logger = logging.getLogger('gadget_glow')


def clear_search_cache():
    try:
        cache.delete('top_selling_products')
        cache.delete('dashboard_stats')
    except Exception as e:
        logger.warning(f"Cache clear error (non-critical): {e}")


@receiver(post_save, sender=Review)
def update_product_rating(sender, instance, **kwargs):
    instance.product.update_rating()
    clear_search_cache()


@receiver(post_save, sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    clear_search_cache()


@receiver(post_delete, sender=Product)
def clear_product_cache_on_delete(sender, instance, **kwargs):
    clear_search_cache()
