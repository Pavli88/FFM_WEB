from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from mysite.forms import RobotParams


# Home page
def home(request):
    robot_form = RobotParams()
    return render(request, 'home.html', {"robot_form": robot_form})


def create_broker(request):

    """
    This process creates new broker account record in the broker table.
    :param request:
    :return:
    """

    return render(request, 'home.html')




