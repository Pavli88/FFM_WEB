from django import forms


class InstrumentForm(forms.Form):
    instrument_name = forms.CharField(label='Instrument Name', max_length=100, required=True)
    instrument_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control form-control-sm '}),
                                        choices=(("Equity", "Equity"),
                                                 ("Commodity", "Commodity"),
                                                 ("Currency", "Currency"),
                                                 ("Bond", "Bond"),
                                                 ("Futures", "Futures")))
    broker = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control form-control-sm '}), choices=(("oanda", "oanda"), ("MAP", "MAP")))