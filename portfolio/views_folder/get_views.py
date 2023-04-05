from django.http import JsonResponse

# Model Imports
from portfolio.models import Portfolio


def get_portfolio(request, port_code):
    if request.method == "GET":
        return JsonResponse(list(Portfolio.objects.filter().values()), safe=False)