from django.apps import AppConfig
import os


class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.listings'
    verbose_name = 'Oferty Nieruchomości'    
    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from .scheduler import start_scheduler
            start_scheduler()