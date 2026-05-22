from celery import shared_task
from django.contrib.auth.models import User
from products.models import Product, Review
from ai_features.services import (
    get_ai_recommendations, analyze_sentiment, generate_product_description
)
import logging

logger = logging.getLogger('gadget_glow')


@shared_task
def generate_recommendations_for_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        get_ai_recommendations(user)
        logger.info(f"Recommendations generated for user {user_id}")
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")


@shared_task
def analyze_review_sentiment(review_id):
    try:
        review = Review.objects.get(id=review_id)
        result = analyze_sentiment(review.comment, review_id)
        logger.info(f"Sentiment analyzed for review {review_id}: {result.get('sentiment')}")
    except Review.DoesNotExist:
        logger.error(f"Review {review_id} not found")


@shared_task
def generate_product_description_task(product_id):
    try:
        product = Product.objects.get(id=product_id)
        description = generate_product_description(
            product.name, product.category.name if product.category else 'General'
        )
        if description:
            product.description = description
            product.save(update_fields=['description'])
        logger.info(f"Description generated for product {product_id}")
    except Product.DoesNotExist:
        logger.error(f"Product {product_id} not found")
