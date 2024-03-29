from .models import Ticket, Review, UserFollows
from django.shortcuts import render, redirect
from django.views import generic
from django.utils import timezone
from app.forms import RegisterForm, LoginForm, FollowForm, TicketForm, ReviewForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.core.files.storage import default_storage
import os
from django.conf import settings
import uuid
from os.path import splitext
from django.db.models import Q


class IndexView(generic.ListView):
    """Feed and Index Management"""

    def get(self, request):
        user = self.request.user

        # following users
        followed_users = UserFollows.objects.filter(user=user).values_list(
            "followed_user", flat=True
        )

        # friends tickets and connected user
        user_and_friends_tickets = (
            Ticket.objects.filter(Q(user=user) | Q(user__in=followed_users))
            .distinct()
            .order_by("-time_created")
        )
        # friends reviews and connected user
        user_and_friends_reviews = (
            Review.objects.filter(Q(user=user) | Q(user__in=followed_users))
            .distinct()
            .order_by("-time_created")
        )

        fake_ticket_id = "fake_ticket"

        # build feed
        feed = {"tickets": {}}
        for ticket in user_and_friends_tickets:
            feed["tickets"][ticket] = {"reviews": []}

        for review in user_and_friends_reviews:
            if review.ticket:
                feed["tickets"].setdefault(review.ticket, {"reviews": []})[
                    "reviews"
                ].append(review)
            else:
                # fake ticket for reviews without ticket
                fake_ticket = {
                    "title": "",
                    "description": "",
                    "time_created": review.time_created,
                }
                fake_ticket_id = "fake_" + str(review.id)
                feed["tickets"][fake_ticket_id] = {
                    "ticket": fake_ticket,
                    "reviews": [review],
                }

        context = {
            "feed": feed,
        }

        return render(self.request, "app/index.html", context)


class Register(generic.FormView):
    """Register Management"""

    template_name = "app/register.html"
    form_class = RegisterForm
    success_url = "/login"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class Login(generic.FormView):
    """Login Management"""

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


class Followers(generic.FormView):
    """Followers Management"""

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


class Posts(generic.FormView):
    """Update and delete Tickets and Reviews"""

    success_url = "posts"

    def get(self, request):
        user = request.user
        ticket_form = TicketForm()
        review_form = ReviewForm()
        tickets = Ticket.objects.filter(user=request.user.id)
        ticket_form.fields["form_type"] = forms.CharField(
            widget=forms.HiddenInput(), initial="create"
        )
        review_form.fields["form_type"] = forms.CharField(
            widget=forms.HiddenInput(), initial="create"
        )
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

        if form_type == "update":
            if ticket_id:
                return self._update_ticket(request.user, ticket_id)
            elif review_id:
                return self._update_review(request.user, review_id)
        elif form_type == "delete":
            if ticket_id:
                self._delete_ticket(
                    ticket_id,
                )
            elif review_id:
                self._delete_review(
                    review_id,
                )
        return redirect("posts")

    def _delete_ticket(self, ticket_id):
        ticket_to_delete = Ticket.objects.get(id=ticket_id)
        ticket_to_delete.delete()

    def _delete_review(self, review_id):
        review_to_delete = Review.objects.get(id=review_id)
        review_to_delete.delete()

    def _update_ticket(self, user, ticket_id):
        tickets = Ticket.objects.filter(user=user.id)
        reviews = Review.objects.filter(user=user.id)
        ticket_data = Ticket.objects.get(id=ticket_id)
        pre_filled_data = {
            "title": ticket_data.ticket,
            "description": ticket_data.description,
        }
        review_form = ReviewForm()
        ticket_form = TicketForm(initial=pre_filled_data)
        ticket_form.fields["form_type"] = forms.CharField(
            widget=forms.HiddenInput(), initial="update"
        )
        ticket_form.fields["ticket"] = forms.CharField(
            widget=forms.HiddenInput(), initial=ticket_data.id
        )
        context = {
            "ticket_form": ticket_form,
            "review_form": review_form,
            "user": user,
            "tickets": tickets,
            "reviews": reviews,
        }
        return render(self.request, "app/posts.html", context)

    def _update_review(self, user, review_id):
        tickets = Ticket.objects.filter(user=user.id)
        reviews = Review.objects.filter(user=user.id)
        review_data = Review.objects.get(id=review_id)
        pre_filled_data = {
            "title": review_data.headline,
            "description": review_data.body,
            "rating": review_data.rating,
        }
        url = "reviews"
        ticket_form = TicketForm()
        review_form = ReviewForm(initial=pre_filled_data)
        review_form.fields["form_type"] = forms.CharField(
            widget=forms.HiddenInput(), initial="update"
        )
        review_form.fields["review"] = forms.CharField(
            widget=forms.HiddenInput(), initial=review_data.id
        )
        context = {
            "ticket_form": ticket_form,
            "review_form": review_form,
            "user": user,
            "tickets": tickets,
            "reviews": reviews,
            "url": url,
        }
        return render(self.request, "app/posts.html", context)


class TicketsManagement(generic.FormView):
    """Create Ticket"""

    success_url = "posts"
    form_class = TicketForm

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form_type = request.POST.get("form_type")
            if form_type == "create":
                return self.form_valid(form)
            elif form_type == "update":
                ticket_id = request.POST.get("ticket")
                return self.form_valid(form, ticket_id=ticket_id)
            else:
                return redirect("posts")
        else:
            return self.form_invalid(form)

    def form_valid(self, form, ticket_id=None):
        user = User.objects.get(username=self.request.user)
        title = form.cleaned_data["title"]
        description = form.cleaned_data["description"]
        image = form.cleaned_data.get("image")
        if ticket_id:
            ticket = Ticket.objects.get(id=ticket_id)
        else:
            ticket = Ticket(user=user)
        ticket.ticket = title
        ticket.description = description
        self.image_upload(image, ticket)
        ticket.save()

        return redirect("posts")

    def image_upload(self, image, ticket):
        if ticket.image:
            old_path = os.path.join(settings.MEDIA_ROOT, ticket.image.name)
            if default_storage.exists(old_path):
                default_storage.delete(old_path)
        if image:
            _, image_extension = splitext(image.name)
            unique_name = f"{uuid.uuid4().hex}{image_extension}"
            default_storage.save(os.path.join(settings.MEDIA_ROOT, unique_name), image)
            ticket.image = unique_name


class ReviewsManagement(generic.FormView):
    """Create Reviews"""

    success_url = "posts"
    form_class = ReviewForm

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form_type = request.POST.get("form_type")
            if form_type == "create":
                return self.form_valid(form)
            elif form_type == "update":
                review_id = request.POST.get("review")
                return self.form_valid(form, review_id=review_id)
            else:
                return redirect("posts")
        else:
            return self.form_invalid(form)

    def form_valid(self, form, review_id=None):
        user = User.objects.get(username=self.request.user)
        title = form.cleaned_data["title"]
        description = form.cleaned_data["description"]
        rating = form.cleaned_data["rating"]
        print(title)
        if review_id:
            review = Review.objects.get(id=review_id)
        else:
            review = Review(user=user)
        review.headline = title
        review.body = description
        review.rating = rating
        review.save()

        return redirect("posts")

    @staticmethod
    def review_from_feed(request):
        if request.method == "POST":
            user = request.user
            review = request.POST.get("description")
            rating = request.POST.get("rating")
            ticket_id = request.POST.get("ticket_id")

            ticket_obj = Ticket.objects.get(id=ticket_id)
            new_review = Review(
                ticket=ticket_obj,
                user=user,
                rating=rating,
                body=review,
                headline="Review de ticket " + ticket_id,
                time_created=timezone.now,
            )
            new_review.save()

        return redirect("flux")
