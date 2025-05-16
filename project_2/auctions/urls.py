from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.create, name="create"),
    path("auction/<int:auction_id>/", views.show_auction, name="show_auction"),
    path("close/<int:auction_id>/", views.close_auction, name="close_auction"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("add_to_watchlist/<int:auction_id>/", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:auction_id>/", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("comment/<int:auction_id>/", views.comment, name="comment"),
    path("display_by_category/", views.display_by_category, name="display_by_category"),

]
