from django.contrib import admin
from django.urls import include, path
from .decorators import unauthenticated_user


from . import views


urlpatterns = [
    path("", views.IndexView.index, name="index"),
    path("register/", unauthenticated_user(views.Register.as_view()), name="register"),
    path("login/", unauthenticated_user(views.Login.as_view()), name="login"),
    path("logout/", views.user_logout, name="logout"),
]
