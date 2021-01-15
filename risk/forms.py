from django import forms


class RobotRiskForm(forms.Form):
    daily_risk = forms.FloatField(label="Daily Risk Limit %", required=True, widget=forms.TextInput(attrs={'id': 'dailyRobotRisk'}))
    daily_number_of_trades = forms.FloatField(label="Daily Max Number of Trades", required=True, widget=forms.TextInput(attrs={'id': 'dailyNmbTrades'}))