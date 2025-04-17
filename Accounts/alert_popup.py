from .models import Reviews


def alert_context(request):
    new_alert = False
    is_admin = False
    alert_id = None

    if request.user.is_authenticated:
        is_admin = request.user.groups.filter(name='admin').exists()

    # Get the latest review with responseAlert=True
    latest_alert = Reviews.objects.filter(
        responseAlert=True).order_by('-created_at').first()

    if latest_alert:
        alert_id = latest_alert.pk
        # Get list of seen alert IDs from session
        seen_alerts = request.session.get('seen_alerts', [])

        # Check if this alert hasn't been seen yet
        if alert_id not in seen_alerts:
            new_alert = True
            # Add to seen alerts when rendering the page
            seen_alerts.append(alert_id)
            request.session['seen_alerts'] = seen_alerts
            request.session.modified = True

    return {
        'new_alert': new_alert,
        'is_admin': is_admin,
        'alert_id': alert_id
    }
