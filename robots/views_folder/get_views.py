from django.http import JsonResponse

# Model Imports
from robots.models import Balance, MonthlyReturns, Robots, RobotTrades


def get_robot(request, id):
    if request.method == "GET":
        print(id)
        return JsonResponse(list(Robots.objects.filter(id=id).values()), safe=False)


def get_robots(request, env):
    if request.method == "GET":
        return JsonResponse(list(Robots.objects.filter(env=env).values()), safe=False)


def get_robot_balance(request):
    if request.method == "GET":
        return JsonResponse(
            list(Balance.objects.filter(robot_id=request.GET.get("id")).filter(date__gte=request.GET.get("start_date")).values()),
            safe=False)


def monthly_returns(request):
    if request.method == 'GET':
        monthly_returns = MonthlyReturns.objects.filter(robot_id=request.GET.get('robot_id'), date__gte=request.GET.get('date') + '-01').order_by('date').values()
        return JsonResponse(list(monthly_returns), safe=False)


def transactions(request):
    if request.method == "GET":
        return JsonResponse(list(RobotTrades.objects.filter(robot=request.GET.get("robot_id")).filter(
            close_time__gte=request.GET.get("start_date")).filter(
            close_time__lte=request.GET.get("end_date")).values()), safe=False)