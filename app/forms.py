from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=65, label="Username", required=True)
    password = forms.CharField(
        max_length=65, label="Password", widget=forms.PasswordInput, required=True
    )


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
