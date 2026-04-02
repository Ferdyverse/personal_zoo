from django import forms
import datetime


class FeedingForm(forms.Form):
    date = forms.DateField(
        label='Date',
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    type = forms.ChoiceField(label='Type', choices=[])
    count = forms.IntegerField(label='Count', min_value=0)
    unit = forms.CharField(label='Unit', required=False)


class FeedingMultiForm(forms.Form):
    date = forms.DateField(
        label='Date',
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    type = forms.ChoiceField(label='Type', choices=[])
    count = forms.IntegerField(label='Count', min_value=0)
    unit = forms.CharField(label='Unit', required=False)
    animals = forms.MultipleChoiceField(label='Animals', choices=[], required=False)
    terrariums = forms.MultipleChoiceField(label='Terrariums', choices=[], required=False)
