import logging
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.listings.models import Property, PriceHistory, Notification
from scraper.parser import fetch_otodom_listing

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        active_properties = Property.objects.filter(is_active = True)
        self.stdout.write(f"Starting price update for {active_properties.count()} active listings...")

        updated_count = 0
        deactivated_count = 0

        for prop in active_properties:
            try:
                # Fetch latest listing details using the scraper parser
                data = fetch_otodom_listing(prop.url)
                if not data:
                    # If data cannot be fetched, mark the listing as inactive (expired/removed)
                    prop.is_active = False
                    prop.save()
                    deactivated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"Deactivated expired/removed listing ID {prop.id} ({prop.url})")
                    )
                    continue

                total_price_raw = data.get('total_price')
                price_sqm_raw = data.get('price_per_sqm')

                if total_price_raw is None:
                    continue

                new_total_price = Decimal(str(total_price_raw))
                new_price_sqm = Decimal(str(price_sqm_raw)) if price_sqm_raw is not None else None

                # Fetch the latest price entry for comparison
                latest_entry = prop.price_history.order_by('-created_at').first()

                # Record new price if it has changed
                if not latest_entry or latest_entry.total_price != new_total_price:
                    PriceHistory.objects.create(
                        property = prop,
                        total_price = new_total_price,
                        price_per_sqm = new_price_sqm
                    )
                    updated_count += 1

                    # Detect price drop and generate user notifications
                    if latest_entry and new_total_price < latest_entry.total_price:
                        price_diff = latest_entry.total_price - new_total_price
                        alert_msg = f"Spadek ceny! Oferta '{prop.title}' staniała o {price_diff} zł (Nowa cena: {new_total_price} zł)."
                        
                        usernames = ", ".join([u.username for u in prop.users.all()])
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"ALERT! Cena spadła o {price_diff} zł dla oferty '{prop.title}' (Użytkownicy: {usernames})"
                            )
                        )

                        # Broadcast notification to all users tracking this property
                        for user in prop.users.all():
                            Notification.objects.create(
                                user = user,
                                property = prop,
                                message = alert_msg
                            )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating property {prop.pk}: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished refreshing. Updated: {updated_count} listings, Deactivated: {deactivated_count} expired listings."
            )
        )