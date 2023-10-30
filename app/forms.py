from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=65, label="Utilisateur", required=True)
    password = forms.CharField(
        max_length=65, label="Mot de passe", widget=forms.PasswordInput, required=True
    )


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields["username"].label = "Utilisateur"
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmer le mot de passe"

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class FollowForm(forms.Form):
    follow_user = forms.CharField(max_length=65, label="Username", required=True)
