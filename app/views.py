from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
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

from django.contrib.auth import logout, login, authenticate
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import IntegrityError

from pprint import pformat


class IndexView(generic.ListView):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            context = {"user": user}
            return render(request, "app/index.html", context)
        else:
            return redirect("login")


class Register(generic.FormView):
    template_name = "app/register.html"
    form_class = RegisterForm
    success_url = "/login"

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            user = form.save()
            return super().form_valid(form)
        else:
            return redirect("/")

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
        next = self.request.POST.get("next")

        if user is not None:
            login(self.request, user)
            if next:
                return redirect(next)
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

    def user_logout(request):
        logout(request)
        return redirect("login")


@method_decorator(login_required(login_url="login"), name="dispatch")
class Followers(generic.FormView):
    def get(self, request):
        form = FollowForm()
        connected_user = request.user
        following = UserFollows.objects.filter(user=connected_user)
        followers = UserFollows.objects.filter(followed_user=connected_user)
        context = {"form": form, "following": following, "followers": followers}
        return render(request, "app/followers.html", context)

    def post(self, request):
        connected_user = request.user
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

    def unfollow_user(request):
        connected_user = request.user.id
        unfollow_user_id = request.POST.get("unfollow_user")
        user_exist = User.objects.filter(pk=unfollow_user_id).exists()
        if user_exist:
            connected_user_object = User.objects.get(pk=connected_user)
            unfollow_user_id_object = User.objects.get(pk=unfollow_user_id)
            try:
                relation = UserFollows.objects.get(
                    user=connected_user_object, followed_user=unfollow_user_id_object
                )
                relation.delete()
            except UserFollows.DoesNotExist:
                messages.error(request, "La relation n'existe pas !")
                return redirect("followers")

            messages.success(request, "Desabonement pris en compte ! ")
            return redirect("followers")
        else:
            messages.error(request, "L'utilisateur n'existe pas")
            return redirect("followers")


@method_decorator(login_required(login_url="login"), name="dispatch")
def infos(request):
    request_str = pformat(vars(request))
    return HttpResponse(f"<pre>{request_str}</pre>")
