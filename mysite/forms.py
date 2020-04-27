from django import forms


class RobotParams(forms.Form):
    robot_name = forms.CharField(label='Your name', max_length=100)

