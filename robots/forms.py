from django import forms


class RobotEntryForm(forms.Form):
    def __init__(self, brokers):
        super(RobotEntryForm, self).__init__()
        self.fields["broker"] = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
                                                  choices=brokers)

    robot_name = forms.CharField(label='Robot Name', max_length=100, required=True)
    strategy = forms.CharField(label='Strategy', max_length=100, required=True)
    broker = forms.ChoiceField()
    environment = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control form-control-sm '}), choices=(("1", "Live"), ("2", "Demo")))
    security = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control form-control-sm '}))
