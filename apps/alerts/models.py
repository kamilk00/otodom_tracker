from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AlertRule(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'alerts')
    city = models.CharField(max_length = 100)
    max_price_per_sqm = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
    min_area_sqm = models.DecimalField(max_digits = 7, decimal_places = 2, null = True, blank = True)
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = "Reguła alertu"
        verbose_name_plural = "Reguły alertów"

    def __str__(self):
        return f"Alert dla {self.user.username}: {self.city} (max {self.max_price_per_sqm} zł/m²)"