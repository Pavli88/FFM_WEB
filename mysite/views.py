from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from mysite.forms import RobotParams


# Home page
def home(request):
    robot_form = RobotParams()
    return render(request, 'home.html', {"robot_form": robot_form})




