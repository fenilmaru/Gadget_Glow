from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ai_features.views import (
    AIRecommendationViewSet, AIChatViewSet,
    SmartSearchViewSet, SentimentViewSet, DescriptionGeneratorViewSet,
)

router = DefaultRouter()
router.register('recommendations', AIRecommendationViewSet, basename='ai-recommendations')
router.register('chat', AIChatViewSet, basename='ai-chat')
router.register('search', SmartSearchViewSet, basename='ai-search')
router.register('sentiment', SentimentViewSet, basename='ai-sentiment')
router.register('describe', DescriptionGeneratorViewSet, basename='ai-describe')

urlpatterns = [
    path('', include(router.urls)),
]
