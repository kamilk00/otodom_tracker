import logging
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.listings.models import Property, PriceHistory, Notification
from scraper.parser import fetch_otodom_listing

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        active_properties = Property.objects.filter(is_active = True)
        self.stdout.write(f"Rozpoczynam odświeżanie cen dla {active_properties.count()} aktywnych ofert...")

        updated_count = 0

        for prop in active_properties:
            data = fetch_otodom_listing(prop.url)
            if not data:
                self.stdout.write(self.style.WARNING(f"Nie udało się pobrać danych dla ID {prop.id} ({prop.url})"))
                continue

            total_price_raw = data.get('total_price')
            price_sqm_raw = data.get('price_per_sqm')

            if total_price_raw is None:
                continue

            new_total_price = Decimal(str(total_price_raw))
            new_price_sqm = Decimal(str(price_sqm_raw)) if price_sqm_raw is not None else None

            latest_entry = prop.price_history.order_by('-created_at').first()

            if not latest_entry or latest_entry.total_price != new_total_price:
                PriceHistory.objects.create(
                    property = prop,
                    total_price = new_total_price,
                    price_per_sqm = new_price_sqm
                )
                updated_count += 1

                if latest_entry and new_total_price < latest_entry.total_price:
                    price_diff = latest_entry.total_price - new_total_price
                    alert_msg = f"Spadek ceny! Oferta '{prop.title}' staniała o {price_diff} zł (Nowa cena: {new_total_price} zł)."
                    
                    usernames = ", ".join([u.username for u in prop.users.all()])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"ALERT! Cena spadła o {price_diff} zł dla oferty '{prop.title}' (Użytkownicy: {usernames})"
                        )
                    )

                    for user in prop.users.all():
                        Notification.objects.create(
                            user = user,
                            property = prop,
                            message = alert_msg
                        )

        self.stdout.write(self.style.SUCCESS(f"Zakończono odświeżanie. Zaktualizowano cenę w {updated_count} ofertach."))