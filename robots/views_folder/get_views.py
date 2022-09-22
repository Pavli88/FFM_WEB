from django.http import JsonResponse

# Model Imports
from robots.models import Balance, MonthlyReturns


def monthly_returns(request):
    if request.method == 'GET':
        monthly_returns = MonthlyReturns.objects.filter(robot_code=request.GET.get('robot_code'), date__gte=request.GET.get('date') + '-01').order_by('date').values()
        return JsonResponse(list(monthly_returns), safe=False)