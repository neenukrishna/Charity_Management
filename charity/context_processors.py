# yourapp/context_processors.py
from .models import Notif

def notification_count(request):
    if request.user.is_authenticated:
        count = Notif.objects.filter(user=request.user, unread=True).count()
    else:
        count = 0
    return {'notification_count': count}
