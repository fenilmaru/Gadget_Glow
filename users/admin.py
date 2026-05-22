from django.contrib import admin
from users.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'role', 'email_verified', 'created_at']
    list_filter = ['role', 'email_verified']
    search_fields = ['user__username', 'phone']
