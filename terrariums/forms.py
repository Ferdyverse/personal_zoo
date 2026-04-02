from django import forms
import datetime


class TerrariumForm(forms.Form):
    name = forms.CharField(max_length=255)
    size = forms.CharField(max_length=255, required=False)
    type = forms.ChoiceField(choices=[])
    notes = forms.CharField(required=False, widget=forms.Textarea())
    image = forms.ImageField(required=False)


class EquipmentForm(forms.Form):
    name = forms.CharField(max_length=255)
    text = forms.CharField(required=False, widget=forms.Textarea())


class LampsForm(forms.Form):
    lamp_type = forms.CharField(label='Type', max_length=255)
    watt = forms.CharField(max_length=50, required=False)
    position = forms.CharField(max_length=255, required=False)
    changed = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )


class EventsForm(forms.Form):
    event = forms.ChoiceField(label='Event', choices=[])
    text = forms.CharField(required=False)
    date = forms.DateField(
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
