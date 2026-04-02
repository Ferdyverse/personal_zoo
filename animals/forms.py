from django import forms

from .models import Animal, AnimalType


class AnimalForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    image = forms.ImageField(required=False)
    birth = forms.CharField(max_length=40, required=False)
    background_color = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'type': 'color'}),
    )

    class Meta:
        model = Animal
        fields = ['name', 'art', 'morph', 'gender', 'birth', 'notes',
                  'image', 'background_color', 'default_ft', 'terrarium']
        widgets = {
            'notes': forms.Textarea(),
        }
