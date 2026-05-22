from rest_framework import serializers
from ai_features.models import AIRecommendation, AIChatSession, AIChatMessage, SentimentAnalysis


class AIRecommendationSerializer(serializers.ModelSerializer):
    product_name = serializers.StringRelatedField(source='product')
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = AIRecommendation
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'score', 'reason', 'created_at']


class AIChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatMessage
        fields = ['id', 'role', 'content', 'metadata', 'created_at']


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, min_length=1, max_length=2000)
    session_id = serializers.CharField(required=False, allow_blank=True)


class SmartSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, min_length=1, max_length=500)


class SentimentSerializer(serializers.ModelSerializer):
    review_text = serializers.CharField(source='review.comment', read_only=True)

    class Meta:
        model = SentimentAnalysis
        fields = ['id', 'review', 'review_text', 'sentiment', 'confidence_score', 'created_at']


class DescriptionGeneratorSerializer(serializers.Serializer):
    product_name = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
    features = serializers.ListField(child=serializers.CharField(), required=False)
