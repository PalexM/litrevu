from django.http import HttpResponse, HttpResponseRedirect
from .models import Ticket, Review, UserFollows
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from app.forms import RegisterForm, LoginForm, FollowForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from app.decorators import unauthenticated_user
from django.contrib.auth import logout, login, authenticate
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import IntegrityError

from pprint import pformat


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


@method_decorator(login_required, name="dispatch")
class Followers(generic.FormView):
    def get(self, request):
        form = (
            FollowForm()
        )  # Asigurați-vă că FollowForm este o clasă validă a formularului definită în Django.
        connected_user = request.user
        following = UserFollows.objects.filter(user=connected_user)
        followers = UserFollows.objects.filter(followed_user=connected_user)
        context = {"form": form, "following": following, "followers": followers}
        return render(request, "app/followers.html", context)

    def post(self, request):
        connected_user = request.user
        if request.POST.get("follow_user"):
            follow_user = request.POST.get("follow_user")
            user_exist = User.objects.filter(username=follow_user).exists()
            if user_exist:
                connected_user_object = User.objects.get(username=connected_user)
                followed_user_object = User.objects.get(username=follow_user)
                try:
                    UserFollows.objects.create(
                        user=connected_user_object, followed_user=followed_user_object
                    )
                except IntegrityError:
                    messages.error(request, "Vous suivez deja cette personne ! ")
                    return redirect("followers")

                messages.success(
                    request, "Felicitations, des a present vous suivez " + follow_user
                )
                return redirect("followers")
            else:
                messages.error(request, "L'utilisateur n'existe pas")
                return redirect("followers")

        elif request.POST.get("unfollow_user"):
            user_pk = request.POST.get("unfollow_user")
            user_exist = User.objects.filter(pk=user_pk)
            if user_exist:
                connected_user_object = User.objects.get(username=connected_user)
                followed_user_object = User.objects.get(username=follow_user)
                try:
                    UserFollows.objects.create(
                        user=connected_user_object, followed_user=followed_user_object
                    )

            return redirect("followers")
            # # # user_exist = User.objects.filter(pk=user_pk)


@login_required
def infos(request):
    request_str = pformat(vars(request))
    return HttpResponse(f"<pre>{request_str}</pre>")
