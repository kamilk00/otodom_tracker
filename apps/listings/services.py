from decimal import Decimal, InvalidOperation
from apps.listings.models import Property, PriceHistory
from scraper.parser import fetch_otodom_listing



def _to_decimal(value: str | int | float | None) -> Decimal | None:
    """safe casting of values to Decimal"""
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _to_int(value: str | int | float | None) -> int | None:
    """safe casting of values to int"""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def save_or_update_listing(url: str, user: User) -> Property | None:
    """
    Fetch property details safely using .get() and associate the listing with a specific user.
    Creates or updates the Property record and appends a PriceHistory entry if price changes.
    """
    data = fetch_otodom_listing(url)
    if not data or not data.get('otodom_id'):
        return None

    # Safely extract scalar and decimal data via .get()
    area_raw = data.get('area_sqm')
    total_price_raw = data.get('total_price')
    price_sqm_raw = data.get('price_per_sqm')

    # Convert numeric fields safely to Decimal
    area_sqm = Decimal(str(area_raw)) if area_raw is not None else Decimal('0')
    total_price = Decimal(str(total_price_raw)) if total_price_raw is not None else None
    price_sqm = Decimal(str(price_sqm_raw)) if price_sqm_raw is not None else None

    # Retrieve existing property or create a new one globally
    property_obj, created = Property.objects.update_or_create(
        otodom_id = data.get('otodom_id'),
        defaults = {
            'title': data.get('title', ''),
            'url': data.get('url', url),
            'city': data.get('city', ''),
            'district': data.get('district') or "",
            'area_sqm': area_sqm,
            'rooms': data.get('rooms'),
            'image_url': data.get('image_url'),
            'is_active': True,
        }
    )

    property_obj.users.add(user)

    # Append price entry if valid price data exists and has changed
    if total_price:
        latest_price_entry = property_obj.price_history.order_by('-created_at').first()

        if not latest_price_entry or latest_price_entry.total_price != total_price:
            PriceHistory.objects.create(
                property = property_obj,
                total_price = total_price,
                price_per_sqm = price_sqm
            )

    return property_obj