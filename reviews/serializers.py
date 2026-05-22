from rest_framework import serializers
from reviews.models import Review
from ai_features.models import SentimentAnalysis


class SentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentimentAnalysis
        fields = ['sentiment', 'confidence_score', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    sentiment = SentimentSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'sentiment', 'is_approved', 'created_at']
        read_only_fields = ['id', 'user', 'is_approved', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate(self, data):
        from reviews.models import Review
        user = self.context['request'].user
        product = data.get('product')
        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this product")
        return data
