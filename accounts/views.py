from django.shortcuts import render
from django.http import HttpResponse


# Accounts main page
def accounts_main(request):
    return render(request, 'accounts/accounts_main.html')
