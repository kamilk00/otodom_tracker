from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Property(models.Model):
    users = models.ManyToManyField(User, related_name = 'tracked_properties')    
    otodom_id = models.CharField(max_length = 64, unique = True, db_index = True)
    title = models.CharField(max_length = 255)
    url = models.URLField(max_length = 500)
    city = models.CharField(max_length = 100, db_index = True)
    district = models.CharField(max_length = 100, blank = True, null = True, db_index = True)
    area_sqm = models.DecimalField(max_digits = 7, decimal_places = 2, help_text = "Powierzchnia w m2")
    rooms = models.IntegerField(blank = True, null = True)
    image_url = models.URLField(max_length = 500, blank = True, null = True)
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = "Nieruchomość"
        verbose_name_plural = "Nieruchomości"

    def __str__(self):
        return f"{self.title} - {self.city}"


class PriceHistory(models.Model):
    property = models.ForeignKey(Property, on_delete = models.CASCADE, related_name = 'price_history')
    total_price = models.DecimalField(max_digits = 12, decimal_places = 2)
    price_per_sqm = models.DecimalField(max_digits = 10, decimal_places = 2)
    created_at = models.DateTimeField(auto_now_add = True, db_index = True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Historia ceny"
        verbose_name_plural = "Historia cen"

    def __str__(self):
        return f"{self.property.title} - {self.total_price} PLN ({self.created_at.strftime('%Y-%m-%d')})"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'notifications')
    property = models.ForeignKey(Property, on_delete = models.SET_NULL, null = True, blank = True)
    message = models.TextField()
    is_read = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"Alert dla {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"