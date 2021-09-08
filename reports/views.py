from django.shortcuts import render


# Main site for reporting
def report_main(request):
    return render(request, 'reports_app/reports_main.html')
