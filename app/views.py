from django.http import HttpResponse, HttpResponseRedirect
from .models import Ticket, Review, UserFollows
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from app.forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from app.decorators import unauthenticated_user
from django.contrib.auth import logout, login, authenticate


@login_required
class IndexView(generic.ListView):
    def index(request):
        user = request.user  # Obține utilizatorul conectat din request
        context = {"user": user}  # Crează un dicționar de context
        return render(
            request, "app/index.html", context
        )  # Transmite contextul către șablon


class Register(generic.FormView):
    template_name = "app/register.html"
    form_class = RegisterForm
    success_url = "/login"

    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class Login(generic.FormView):
    template_name = "app/login.html"
    form_class = LoginForm
    success_url = "/"

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            # Aici poți gestiona cazul în care autentificarea a eșuat
            return self.form_invalid(form)


def user_logout(request):
    logout(request)
    return redirect("login")
