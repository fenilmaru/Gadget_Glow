from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ai_features.models import AIRecommendation, AIChatSession, AIChatMessage, SentimentAnalysis
from ai_features.serializers import (
    AIRecommendationSerializer, AIChatMessageSerializer,
    ChatRequestSerializer, SmartSearchSerializer,
    SentimentSerializer, DescriptionGeneratorSerializer,
)
from ai_features.services import (
    get_ai_recommendations, ai_chatbot_response,
    smart_search, analyze_sentiment, generate_product_description,
)
from reviews.models import Review
from products.models import Product
from products.serializers import ProductListSerializer


class AIRecommendationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        recommendations = get_ai_recommendations(request.user)
        serializer = AIRecommendationSerializer(recommendations, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def for_product(self, request):
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)

        from products.services import get_related_products
        try:
            product = Product.objects.get(id=product_id)
            related = Product.objects.filter(
                category=product.category, is_active=True, is_deleted=False
            ).exclude(id=product_id)[:6]
            serializer = ProductListSerializer(related, many=True, context={'request': request})
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class AIChatViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def chat(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = ai_chatbot_response(
            user=request.user,
            message=serializer.validated_data['message'],
            session_id=serializer.validated_data.get('session_id'),
        )
        return Response(result)

    @action(detail=False, methods=['get'])
    def history(self, request):
        sessions = AIChatSession.objects.filter(user=request.user, is_active=True)[:5]
        data = []
        for session in sessions:
            messages = AIChatMessage.objects.filter(session=session)[:20]
            data.append({
                'session_id': session.session_id,
                'messages': AIChatMessageSerializer(messages, many=True).data,
                'created_at': session.created_at,
            })
        return Response(data)


class SmartSearchViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def search(self, request):
        serializer = SmartSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        results = smart_search(serializer.validated_data['query'])
        product_serializer = ProductListSerializer(results, many=True, context={'request': request})
        return Response({'results': product_serializer.data, 'count': len(results)})


class SentimentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        review_id = request.data.get('review_id')
        if not review_id:
            return Response({'error': 'review_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

        result = analyze_sentiment(review.comment, review_id)
        return Response(result)


class DescriptionGeneratorViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = DescriptionGeneratorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        description = generate_product_description(
            serializer.validated_data['product_name'],
            serializer.validated_data['category'],
            serializer.validated_data.get('features'),
        )
        return Response({'description': description})
