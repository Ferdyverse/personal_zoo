from django import forms
import datetime


class HistoryForm(forms.Form):
    date = forms.DateField(
        label='Date',
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    event = forms.ChoiceField(label='Event', choices=[])
    text = forms.CharField(label='Text', required=False, widget=forms.TextInput())


class HistoryMultiForm(forms.Form):
    date = forms.DateField(
        label='Date',
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    event = forms.ChoiceField(label='Event', choices=[])
    text = forms.CharField(label='Text', required=False)
    animals = forms.MultipleChoiceField(label='Animals', choices=[], required=False)
    terrariums = forms.MultipleChoiceField(label='Terrariums', choices=[], required=False)
