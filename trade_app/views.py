from django.shortcuts import render

# Main site for trading
def trade_main(request):
    return render(request, 'trade/trade_main.html')
