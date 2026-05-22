import json
import logging
import re
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q, Min, Max

from products.models import Product, Category, Brand
from ai_features.models import AIRecommendation, AIChatSession, AIChatMessage, SentimentAnalysis
from orders.models import Order

logger = logging.getLogger('gadget_glow')
_client = None


def _get_client():
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        from openai import OpenAI
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def get_ai_recommendations(user, limit=8):
    cache_key = f'ai_recommendations_{user.id}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    existing = AIRecommendation.objects.filter(user=user)[:limit]
    if existing.count() >= limit:
        return existing

    from orders.models import OrderItem
    purchased_ids = OrderItem.objects.filter(order__user=user).values_list('product_id', flat=True)
    purchased_categories = Product.objects.filter(
        id__in=purchased_ids
    ).values_list('category_id', flat=True).distinct()

    if purchased_categories:
        similar = Product.objects.filter(
            category_id__in=purchased_categories,
            is_active=True,
            is_deleted=False
        ).exclude(id__in=purchased_ids).order_by('-rating')[:limit]
    else:
        similar = Product.objects.filter(
            is_featured=True, is_active=True, is_deleted=False
        ).order_by('-rating')[:limit]

    for i, product in enumerate(similar):
        AIRecommendation.objects.update_or_create(
            user=user, product=product,
            defaults={'score': 1.0 - (i * 0.05), 'reason': 'Based on your preferences'}
        )

    results = existing[:limit]
    cache.set(cache_key, list(results), 3600)
    return results


def _local_chatbot_response(message, user):
    """Handle common queries using local database lookups when OpenAI is unavailable."""
    msg_lower = message.lower().strip()

    # Category keyword mapping (must match actual category names in DB)
    cat_keywords = {
        'mobile case': 'Mobile Cases', 'cases': 'Mobile Cases', 'case': 'Mobile Cases',
        'cover': 'Mobile Cases', 'back cover': 'Mobile Cases',
        'charger': 'Chargers', 'charging': 'Chargers', 'adapter': 'Chargers', 'power adapter': 'Chargers',
        'cable': 'Cables', 'cables': 'Cables', 'usb': 'Cables', 'lightning': 'Cables', 'usb-c': 'Cables',
        'power bank': 'Power Banks', 'powerbank': 'Power Banks', 'portable charger': 'Power Banks',
        'watch': 'Smart Watches', 'smartwatch': 'Smart Watches', 'fitness band': 'Smart Watches',
        'holder': 'Phone Holders', 'stand': 'Phone Holders', 'mount': 'Phone Holders', 'phone stand': 'Phone Holders',
    }

    # Greeting patterns
    if any(w in msg_lower for w in ['hi', 'hello', 'hey', 'good morning', 'good evening']):
        return "Hello! Welcome to Gadget Glow. I can help you find products, check prices, track orders, and more. What can I help you with?"

    # Help intent
    if any(w in msg_lower for w in ['help', 'what can you do', 'capabilities']):
        return ("I can help you with:\n"
                "• 🔍 Find products by category or keyword\n"
                "• 💰 Check prices and deals\n"
                "• 📦 Track your orders\n"
                "• ⭐ Recommend trending products\n"
                "• 📋 Compare product features\n\n"
                "Try asking: 'Show me chargers' or 'Best power banks under ₹1000'")

    # Greetings that mention the store
    if 'gadget' in msg_lower or 'glow' in msg_lower or 'store' in msg_lower:
        return ("Welcome to Gadget Glow – your premium mobile accessories destination! "
                "We offer top-quality phone cases, chargers, cables, power banks, smart watches, and phone holders. "
                "What are you looking for today?")

    # Order tracking
    if any(w in msg_lower for w in ['track', 'order', 'my order', 'where is my', 'shipping', 'delivery']):
        orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
        if orders:
            lines = ['Here are your recent orders:']
            for o in orders:
                lines.append(f"  • Order #{o.id}: {o.status.title()} — ₹{o.total_price}")
            lines.append("Use a tracking number for detailed updates.")
            return '\n'.join(lines)
        return "You don't have any orders yet. Browse our products and place your first order today!"

    # Trending / bestsellers
    if any(w in msg_lower for w in ['trending', 'bestseller', 'popular', 'top rated', 'best', 'hot']):
        products = Product.objects.filter(is_active=True, is_deleted=False).order_by('-rating')[:6]
        if products:
            lines = ['Here are our top-rated products:']
            for p in products:
                cat_name = p.category.name if p.category else 'Accessories'
                lines.append(f"  • {p.name} — ₹{p.price} ⭐{p.rating} ({cat_name})")
            return '\n'.join(lines)
        return "We have a great collection of products. Browse our catalog to find what you need!"

    # Deals / discounts / offers
    if any(w in msg_lower for w in ['deal', 'discount', 'offer', 'sale', 'coupon', 'promo', 'cheap', 'budget']):
        products = Product.objects.filter(is_active=True, is_deleted=False, compare_price__gt=0).order_by('-compare_price')[:6]
        if products:
            lines = ['Here are our best deals:']
            for p in products:
                discount = p.discount_percentage
                lines.append(f"  • {p.name} — ₹{p.price} (was ₹{p.compare_price}, save {discount}%!)")
            lines.append("\nUse coupon code WELCOME10 for 10% off your first order!")
            return '\n'.join(lines)
        return "Check our product catalog for the latest deals and discounts!"

    # New arrivals
    if any(w in msg_lower for w in ['new', 'arrival', 'latest', 'just launched', 'new product']):
        products = Product.objects.filter(is_active=True, is_deleted=False).order_by('-created_at')[:6]
        if products:
            lines = ['Our newest arrivals:']
            for p in products:
                lines.append(f"  • {p.name} — ₹{p.price}")
            return '\n'.join(lines)
        return "Check our product catalog for the latest arrivals!"

    # Detect price constraint and matched categories
    price_match = re.search(r'(?:under|below|less than|upto|up to)\s*(?:₹|rs\.?\s*)?(\d+)', msg_lower)
    max_price = float(price_match.group(1)) if price_match else None

    matched_cats = []
    for keyword, cat_name in cat_keywords.items():
        if keyword in msg_lower:
            matched_cats.append(cat_name)
    matched_cats = list(set(matched_cats))

    # Category-specific queries (optionally combined with price)
    if matched_cats:
        lines = []
        for cat_name in matched_cats[:2]:
            qs = Product.objects.filter(category__name=cat_name, is_active=True, is_deleted=False)
            if max_price:
                qs = qs.filter(price__lte=max_price)
                label = f'**{cat_name} under ₹{int(max_price)}:**'
            else:
                label = f'**{cat_name}:**'
            products = qs.order_by('-rating')[:5]
            if products:
                lines.append(label)
                for p in products:
                    lines.append(f"  • {p.name} — ₹{p.price} ⭐{p.rating}")
                lines.append('')
        if lines:
            lines.append("Browse more categories on our Products page!")
            return '\n'.join(lines)
        if max_price:
            cat_list = ', '.join(matched_cats[:2])
            return (f"I couldn't find any {cat_list} under ₹{int(max_price)}. "
                    f"Try browsing our Products page or increasing your budget.")

    # Price range queries only (no category match)
    if max_price:
        products = Product.objects.filter(is_active=True, is_deleted=False, price__lte=max_price)[:6]
        if products:
            lines = [f'Products under ₹{int(max_price)}:']
            for p in products:
                lines.append(f"  • {p.name} — ₹{p.price} ⭐{p.rating}")
            return '\n'.join(lines)
        return f"Sorry, we don't have products under ₹{int(max_price)} right now. Try a higher budget?"

    # Generic product query (search by any remaining keywords)
    words = [w for w in msg_lower.split() if len(w) > 2]
    if words:
        q = Q()
        for w in words:
            q |= Q(name__icontains=w) | Q(description__icontains=w) | Q(category__name__icontains=w)
        products = Product.objects.filter(q, is_active=True, is_deleted=False)[:5]
        if products:
            lines = [f'I found these products matching your search:']
            for p in products:
                cat_name = p.category.name if p.category else ''
                lines.append(f"  • {p.name} — ₹{p.price} ({cat_name})")
            return '\n'.join(lines)

    # Fallback
    return ("I'm not sure I understood. Here's what I can help with:\n"
            "• Ask for products: 'Show me power banks' or 'Best phone cases'\n"
            "• Check prices: 'Chargers under ₹500'\n"
            "• Track orders: 'Track my order'\n"
            "• Get recommendations: 'What's trending?'")


def ai_chatbot_response(user, message, session_id=None):
    if not session_id:
        import uuid
        session_id = uuid.uuid4().hex[:16]

    session, _ = AIChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={'user': user}
    )

    AIChatMessage.objects.create(session=session, role='user', content=message)

    # Try OpenAI first
    try:
        client = _get_client()
        system_prompt = """You are GadgetBot, an AI shopping assistant for Gadget Glow - a mobile accessories e-commerce platform. 
Help users with:
1. Product recommendations (chargers, phone cases, cables, power banks, smart watches, phone holders)
2. Order tracking and support
3. Product comparisons
4. Technical specifications
5. General shopping advice

Be helpful, concise, and friendly. For product queries, suggest checking the product catalog for current prices and availability."""

        messages = [{'role': 'system', 'content': system_prompt}]
        history = session.messages.order_by('-created_at')[:10]
        for msg in reversed(history):
            messages.append({'role': msg.role, 'content': msg.content})

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        reply = response.choices[0].message.content
        AIChatMessage.objects.create(session=session, role='assistant', content=reply)
        return {'reply': reply, 'session_id': session_id}

    except Exception as e:
        logger.error(f"AI Chatbot error (falling back to local): {e}")
        # Use local database-driven response
        reply = _local_chatbot_response(message, user)
        AIChatMessage.objects.create(session=session, role='assistant', content=reply)
        return {'reply': reply, 'session_id': session_id}


def smart_search(query):
    cache_key = f'smart_search:{query}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {'role': 'system', 'content': 'Extract search filters from the query. Return JSON with: search_term, max_price, min_price, category. If not specified, set to null.'},
                {'role': 'user', 'content': query}
            ],
            response_format={'type': 'json_object'},
            max_tokens=200,
        )
        filters = json.loads(response.choices[0].message.content)
    except Exception:
        filters = {'search_term': query, 'max_price': None, 'min_price': None, 'category': None}

    qs = Product.objects.filter(is_active=True, is_deleted=False)
    if filters.get('search_term'):
        qs = qs.filter(
            Q(name__icontains=filters['search_term']) |
            Q(description__icontains=filters['search_term'])
        )
    if filters.get('max_price'):
        qs = qs.filter(price__lte=filters['max_price'])
    if filters.get('min_price'):
        qs = qs.filter(price__gte=filters['min_price'])
    if filters.get('category'):
        qs = qs.filter(category__name__icontains=filters['category'])

    results = qs.order_by('-rating')[:20]
    cache.set(cache_key, list(results), 600)
    return results


def analyze_sentiment(review_text, review_id):
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {'role': 'system', 'content': 'Analyze the sentiment of this product review. Return JSON with: sentiment (positive/negative/neutral), confidence_score (0-1), key_points (list).'},
                {'role': 'user', 'content': review_text}
            ],
            response_format={'type': 'json_object'},
            max_tokens=200,
        )
        result = json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        result = {'sentiment': 'neutral', 'confidence_score': 0.5, 'key_points': []}

    SentimentAnalysis.objects.update_or_create(
        review_id=review_id,
        defaults={
            'sentiment': result.get('sentiment', 'neutral'),
            'confidence_score': result.get('confidence_score', 0.5),
            'analysis_details': result,
        }
    )

    return result


def generate_product_description(product_name, category, features=None):
    try:
        client = _get_client()
        prompt = f"Generate an SEO-friendly product description for a {product_name} in the {category} category."
        if features:
            prompt += f" Key features: {', '.join(features)}."
        prompt += " Include specifications, benefits, and a compelling call to action."

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=400,
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Description generation error: {e}")
        return f"High-quality {product_name} - perfect for your needs. Check product details for specifications."
