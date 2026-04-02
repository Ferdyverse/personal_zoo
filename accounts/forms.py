from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import User


class RegisterForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=40)
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        min_length=6,
        max_length=25,
    )
    confirm = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput,
        min_length=6,
        max_length=25,
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already registered')
        return email

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm')
        if pw and confirm and pw != confirm:
            self.add_error('confirm', 'Passwords must match.')
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class PasswordForm(forms.Form):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput)
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput,
        min_length=6,
        max_length=25,
    )
    confirm = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput,
        min_length=6,
        max_length=25,
    )

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm')
        if pw and confirm and pw != confirm:
            self.add_error('confirm', 'Passwords must match.')
        return cleaned_data
