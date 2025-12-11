from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from recipes.models.comment import Notification


@login_required
def mark_notification_read(request, notification_id):
    """
    Mark the notification as read once it has been clicked
    """
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.is_read = True
    notif.save()

    return redirect(notif.link)