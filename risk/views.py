from mysite.views import *

# Main site for risk management
def risk_main(request):
    return render(request, 'risk_app/risk_main.html', {"robots": robots,
                                                       "risk_form": risk_form})
