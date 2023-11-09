from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from .models import Ticket, Review, UserFollows
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from app.forms import RegisterForm, LoginForm, FollowForm, TicketForm, ReviewForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth import logout, login, authenticate
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import IntegrityError
import os
from django.conf import settings
from pprint import pformat
from django.utils.text import slugify
import uuid
from os.path import splitext


class IndexView(generic.ListView):
    def get(self, request):
        user = request.user
        context = {"user": user}
        return render(request, "app/index.html", context)


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


class TicketsAndReviews(generic.FormView):
    success_url = "tickets"

    def get(self, request):
        user = request.user
        ticket_form = TicketForm()
        review_form = ReviewForm()
        review_form.fields["form_type"] = forms.CharField(
            widget=forms.HiddenInput(), initial="update"
        )
        tickets = Ticket.objects.filter(user=request.user.id)
        reviews = Review.objects.filter(user=request.user.id)
        context = {
            "tickets": tickets,
            "reviews": reviews,
            "ticket_form": ticket_form,
            "review_form": review_form,
            "user": user,
        }
        return render(request, "app/posts.html", context)

    def post(self, request):
        form_type = request.POST.get("form_type")
        ticket_id = request.POST.get("ticket")
        review_id = request.POST.get("review")
        match form_type:
            case "delete":
                if ticket_id:
                    self._delete_ticket(ticket_id)
                elif review_id:
                    self._delete_review(review_id)
            case "update":
                if ticket_id:
                    self._update_ticket(ticket_id)
                elif review_id:
                    self._update_review(review_id)
        return redirect("tickets")

    def _delete_ticket(self, ticket_id):
        ticket_to_delete = Ticket.objects.get(id=ticket_id)
        ticket_to_delete.delete()
        return redirect("tickets")

    def _delete_review(self, review_id):
        review_to_delete = Review.objects.get(id=review_id)
        review_to_delete.delete()
        return redirect("tickets")

    def _update_ticket(self, ticket_id):
        pass

    def _update_review(self, review_id):
        pass

    # def _get_ticket_form(self, request):
    #     user = request.user
    #     pre_filled_data = {
    #         "title": "Valoare pre-umplută pentru titlu",
    #         "description": "Valoare pre-umplută pentru descriere",
    #     }
    #     form = ReviewForm(initial=pre_filled_data)
    #     context = {"form": form, "user": user}
    #     return render(request, "app/posts.html", context)

    # def post(self, request):
    #     connected_user = self.request.user
    #     title = self.request.POST.get("title")
    #     description = self.request.POST.get("description")
    #     image = self.request.FILES.get("image")
    #     _, image_extension = splitext(image.name)
    #     unique_name = f"{str(uuid.uuid4().hex)}{image_extension}"
    #     with open(
    #         os.path.join(settings.MEDIA_ROOT, "media", unique_name), "wb"
    #     ) as destination:
    #         for chunk in image.chunks():
    #             destination.write(chunk)
    #     return redirect("tickets")
