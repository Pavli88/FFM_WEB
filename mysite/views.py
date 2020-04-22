from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


# Home page
def home(request):
    return render(request, 'home.html')




