from django.urls import path
from django.contrib.auth.decorators import login_required
from .decorators import redirect_connected_user
from django.conf import settings
from django.conf.urls.static import static


from . import views


urlpatterns = [
    path("", login_required(views.IndexView.as_view()), name="index"),
    path("flux/", login_required(views.IndexView.as_view()), name="flux"),
    path(
        "register/", redirect_connected_user(views.Register.as_view()), name="register"
    ),
    path("login/", redirect_connected_user(views.Login.as_view()), name="login"),
    path("logout/", login_required(views.Login.user_logout), name="logout"),
    path("followers/", login_required(views.Followers.as_view()), name="followers"),
    path("unfollow/", login_required(views.Followers.unfollow_user), name="unfollow"),
    path("posts/", login_required(views.Posts.as_view()), name="posts"),
    path("tickets/", login_required(views.TicketsManagement.as_view()), name="tickets"),
    path("reviews/", login_required(views.ReviewsManagement.as_view()), name="reviews"),
    path(
        "review/",
        login_required(views.ReviewsManagement.review_from_feed),
        name="review",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# path("posts/") List toutes les posts et creation des formulaires
# path (tickets/) create, update, delete
# path (reviews) create, update, delete
#
