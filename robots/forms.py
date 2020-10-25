from django import forms


class RobotEntryForm(forms.Form):
    robot_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), label='Robot Name', max_length=100, required=True)
    strategy = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), label='Strategy', max_length=100, required=True)
    broker = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control form-control-sm '}), choices=(("oanda", "oanda"), ("MAP", "MAP")))
    environment = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control form-control-sm '}), choices=(("live", "Live"), ("demo", "Demo")))
    security = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control form-control-sm '}), required=True)
    account_number = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control form-control-sm '}), required=True)
