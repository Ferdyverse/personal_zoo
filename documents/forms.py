from django import forms


class DocumentForm(forms.Form):
    name = forms.CharField(max_length=255)
    filename = forms.FileField()
