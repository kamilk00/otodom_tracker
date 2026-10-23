def unread_notifications(request):
    """Injects unread notification count globally into all templates."""
    if request.user.is_authenticated:
        return {
            'unread_alerts_count': request.user.notifications.filter(is_read = False).count()
        }
    return {'unread_alerts_count': 0}