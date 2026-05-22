from django.contrib import admin
from .models import AIRecommendation

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'score', 'created_at']
    list_filter = ['score']
    search_fields = ['user__username', 'product__name']
