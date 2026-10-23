import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.contrib.auth.forms import UserCreationForm
from .models import Property, PriceHistory, Notification
from .forms import AddPropertyForm
from .services import save_or_update_listing


@login_required
def property_list(request):
    """Render the authenticated user's tracked listings and handle URL submission."""
    if request.method == 'POST':
        form = AddPropertyForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            property_obj = save_or_update_listing(url, request.user)
            if property_obj:
                messages.success(request, "Pomyślnie dodano ofertę do Twojej listy!")
                return redirect('listings:property_detail', pk = property_obj.pk)
            else:
                messages.error(request, "Nie udało się pobrać danych z podanego linku.")
    else:
        form = AddPropertyForm()

    # Filter properties strictly by the current logged-in user
    properties = Property.objects.filter(users = request.user, is_active = True).prefetch_related(
        Prefetch('price_history', queryset = PriceHistory.objects.order_by('-created_at'))
    )
    
    unread_notifications = request.user.notifications.filter(is_read = False)

    context = {
        'properties': properties,
        'form': form,
        'unread_notifications': unread_notifications, # <-- dodaj to
    }

    return render(request, 'listings/property_list.html', context)


@login_required
@login_required
def property_detail(request, pk):
    """Render detail page for a property owned by the logged-in user."""
    property_obj = get_object_or_404(
        Property.objects.filter(users = request.user).prefetch_related('price_history'),
        pk = pk
    )
    
    Notification.objects.filter(user = request.user, property = property_obj, is_read = False).update(is_read = True)
    
    price_history = property_obj.price_history.order_by('created_at')
    
    chart_labels = [entry.created_at.strftime('%Y-%m-%d %H:%M') for entry in price_history]
    chart_data = [float(entry.total_price) for entry in price_history]

    return render(request, 'listings/property_detail.html', {
        'property': property_obj,
        'price_history': price_history,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_data_json': json.dumps(chart_data),
    })


@login_required
def property_delete(request, pk):
    """Delete a property listing owned by the logged-in user."""
    property_obj = get_object_or_404(Property, pk = pk, users = request.user)

    if request.method == 'POST':
        property_obj.users.remove(request.user)
        messages.success(request, "Oferta została usunięta z Twoich obserwowanych.")
        return redirect('listings:property_list')
        
    return render(request, 'listings/property_confirm_delete.html', {'property': property_obj})


def register(request):
    """Handle new user registration using Django's built-in UserCreationForm."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Konto dla {username} zostało utworzone! Możesz się zalogować.")
            return redirect('login')
    else:
        form = UserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})