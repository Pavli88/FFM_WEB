from django.shortcuts import render


def instruments_main(request):
    return render(request, 'instruments/instruments_main.html')

