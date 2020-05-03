from django.shortcuts import render


# Main site for portfolios
def portfolios_main(request):
    return render(request, 'portfolios/portfolios_main.html')
