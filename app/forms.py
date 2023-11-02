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
    follow_user = forms.CharField(max_length=65, label="Utilisateur", required=True)


class TicketForm(forms.Form):
    title = forms.CharField(max_length=128, label="Titre", required=True)
    description = forms.CharField(
        widget=forms.Textarea, label="Description", required=True
    )
    image = forms.ImageField(label="Image", required=False)


class ReviewForm(forms.Form):
    title = forms.CharField(max_length=128, label="Titre", required=True)
    description = forms.CharField(
        widget=forms.Textarea, label="Description", required=True
    )
    rating_choices = [(i, i) for i in range(5)]
    rating = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=rating_choices,
    )
