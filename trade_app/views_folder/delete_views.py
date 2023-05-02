from trade_app.models import Notifications
from django.http import JsonResponse


def delete_notifications(request):
    if request.method == "GET":
        Notifications.objects.filter().delete()
        return JsonResponse({'response': 'Signals are deleted'}, safe=False)