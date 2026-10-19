from django.shortcuts import render, get_object_or_404
from .models import Property


def property_list(request):
    """Lista wszystkich aktywnych nieruchomości w bazie."""
    properties = Property.objects.filter(is_active = True).order_by('-updated_at')
    return render(request, 'listings/property_list.html', {'properties': properties})


def property_detail(request, pk):
    """Szczegóły wybranej nieruchomości wraz z pełną historią cen."""
    prop = get_object_or_404(Property, pk = pk)
    price_history = prop.price_history.all()
    return render(request, 'listings/property_detail.html', {
        'property': prop,
        'price_history': price_history,
    })