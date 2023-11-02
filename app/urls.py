from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from .decorators import redirect_connected_user


from . import views


urlpatterns = [
    path("", login_required(views.IndexView.as_view()), name="index"),
    path(
        "register/", redirect_connected_user(views.Register.as_view()), name="register"
    ),
    path("login/", redirect_connected_user(views.Login.as_view()), name="login"),
    path("logout/", login_required(views.Login.user_logout), name="logout"),
    path("followers/", login_required(views.Followers.as_view()), name="followers"),
    path("unfollow/", login_required(views.Followers.unfollow_user), name="unfollow"),
    path("tickets/", login_required(views.Tickets.as_view()), name="tickets"),
]
