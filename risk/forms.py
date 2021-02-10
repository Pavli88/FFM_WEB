from django import forms


class RobotRiskForm(forms.Form):
    daily_risk = forms.FloatField(label="Daily Loss Limit %", required=True, widget=forms.TextInput(attrs={'id': 'dailyRobotRisk'}))
    daily_number_of_trades = forms.FloatField(label="Daily Max Number of Trades", required=True, widget=forms.TextInput(attrs={'id': 'dailyNmbTrades'}))
    risk_per_trade = forms.FloatField(label="Risk per Trade %", required=True,
                                  widget=forms.TextInput(attrs={'id': 'riskPerTrade'}))
    pyramiding_level = forms.IntegerField(label="Pyramiding Level", required=True,
                                      widget=forms.TextInput(attrs={'id': 'pyramidingLevel'}))
    choices = (('Stop Based', 'Stop Based'), ('Fix', 'Fix'),)
    quantity_type = forms.ChoiceField(choices=choices, label="Quantity Type", required=True,
                                          widget=forms.Select(attrs={'id': 'quantityType'}))
    quantity = forms.IntegerField(label="Quantity", required=True,
                                       widget=forms.TextInput(attrs={'id': 'quantity'}))