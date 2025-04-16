from .models import Reviews


def alert_context(request):
    new_alert = False
    is_admin = False

    if request.user.is_authenticated:
        is_admin = request.user.groups.filter(name='admin').exists()

    # Check for alerts every time
    new_alert = Reviews.objects.filter(responseAlert=True).exists()

    return {
        'new_alert': new_alert,
        'is_admin': is_admin
    }
