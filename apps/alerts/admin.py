from django.contrib import admin
from .models import AlertRule


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'max_price_per_sqm', 'min_area_sqm', 'is_active', 'created_at')
    list_filter = ('is_active', 'city')
    search_fields = ('user__username', 'user__email', 'city')