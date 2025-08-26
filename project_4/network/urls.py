
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("profile/<int:user_id>", views.profile_view, name="profile"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("following", views.following_view, name="following"),


    # API things
    path("like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path("follow/<int:user_id>", views.toggle_follow, name="follow"),
    path("edit_post/<int:post_id>/", views.edit_post, name="edit_post"),
    path("edit_profile/<int:user_id>/", views.edit_profile, name="edit_profile"),
]
