from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from .models import Property, PriceHistory


def property_list(request):
    """Render a list of all active property listings with their latest prices."""
    properties = Property.objects.filter(is_active=True).prefetch_related(
        Prefetch('price_history', queryset=PriceHistory.objects.order_by('-created_at'))
    )
    
    return render(request, 'listings/property_list.html', {
        'properties': properties
    })


def property_detail(request, pk):
    """Render detail page for a single property with price history records."""
    property_obj = get_object_or_404(
        Property.objects.prefetch_related('price_history'),
        pk=pk
    )
    
    # Retrieve price history sorted chronologically for charting
    price_history = property_obj.price_history.order_by('created_at')
    
    return render(request, 'listings/property_detail.html', {
        'property': property_obj,
        'price_history': price_history,
    })