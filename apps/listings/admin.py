from django.contrib import admin

from .models import Property, PriceHistory


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ('created_at',)
    can_delete = False


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'district', 'area_sqm', 'rooms', 'is_active', 'updated_at')
    list_filter = ('city', 'is_active', 'rooms')
    search_fields = ('title', 'otodom_id', 'city', 'district')
    inlines = [PriceHistoryInline]


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('property', 'total_price', 'price_per_sqm', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('property__title', 'property__otodom_id')
    readonly_fields = ('created_at',)