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


def save_or_update_listing(url: str) -> Property | None:
    data = fetch_otodom_listing(url)
    if not isinstance(data, dict):
        return None

    otodom_id = data.get("otodom_id")
    if not otodom_id:
        print("Brak otodom_id w przekazanych danych.")
        return None

    area_sqm = _to_decimal(data.get("area_sqm"))
    total_price = _to_decimal(data.get("total_price"))
    price_per_sqm = _to_decimal(data.get("price_per_sqm"))
    rooms = _to_int(data.get("rooms"))

    if area_sqm is None or total_price is None or price_per_sqm is None:
        print(f"Brak kluczowych danych liczbowych (cena/metraż) dla ID: {otodom_id}")
        return None

    defaults = {
        "title": data.get("title") or "Brak tytułu",
        "url": data.get("url") or url,
        "city": data.get("city") or "Nieokreślone",
        "district": data.get("district") or "",
        "area_sqm": area_sqm,
        "rooms": rooms,
        "image_url": data.get("image_url") or "",
    }

    # save or download property data
    prop, created = Property.objects.get_or_create(
        otodom_id=str(otodom_id),
        defaults=defaults
    )

    # fields update
    if not created:
        for key, value in defaults.items():
            setattr(prop, key, value)
        prop.save()

    # save price history
    last_history = prop.price_history.first()

    if not last_history or last_history.total_price != total_price:
        PriceHistory.objects.create(
            property = prop,
            total_price = total_price,
            price_per_sqm = price_per_sqm
        )

    return prop