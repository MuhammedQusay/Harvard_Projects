from urllib import request
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Auction, Bid, Comment


def index(request):
    auctions = Auction.objects.all()
    return render(request, "auctions/index.html", {
        "auctions": auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.method == "POST":
        user = request.user
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        bid = request.POST.get("bid")
        imageURL = request.POST.get("imageURL")
        if not imageURL:
            imageURL = "https://www.svgrepo.com/show/340721/no-image.svg"

        bid = Bid(user=user, bid_amount=bid)
        bid.save()

        auction = Auction(user=user, title=title, description=description, category=category, current_bid=bid, img=imageURL)
        auction.save()

        return redirect("show_auction", auction_id=auction.id)


    category_choices = Auction.CATEGORY_CHOICES
    return render(request, "auctions/create.html", {
        "category_choices": category_choices
    })


def show_auction(request, auction_id):
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return render(request, "auctions/auction.html", {
            "error": "This page does not exist.",
        })

    comments = auction.comments.all().order_by("-date")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return render(request, "auctions/auction.html", {
                "error": "Please login to be able to bid and Comment.",
                "auction" : auction,
                "comments" : comments,
                })

        new_bid = int(request.POST.get("new_bid"))

        if auction.current_bid.bid_amount >= new_bid:
            return render(request, "auctions/auction.html", {
                    "error": "Bid not high enough!",
                    "auction" : auction,
                    "comments" : comments,
                    })

        bid = Bid(user=request.user, bid_amount=new_bid)
        bid.save()

        auction.current_bid = bid
        auction.save()

    return render(request, "auctions/auction.html", {
        "auction" : auction,
        "comments" : comments,
        })

@login_required(login_url="login")
def close_auction(request, auction_id):
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return render(request, "auctions/auction.html", {
            "error": "This page does not exist.",
        })
    auction.is_active = False
    auction.save()

    return redirect("show_auction", auction_id)

@login_required(login_url="login")
def add_to_watchlist(request, auction_id):
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return render(request, "auctions/auction.html", {
            "error": "This page does not exist.",
        })

    auction.watchlist.add(request.user)

    return redirect("show_auction", auction_id)


@login_required(login_url="login")
def remove_from_watchlist(request, auction_id):
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return render(request, "auctions/auction.html", {
            "error": "This page does not exist.",
        })

    auction.watchlist.remove(request.user)

    return redirect("show_auction", auction_id)


@login_required(login_url="login")
def watchlist(request):
    auctions = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "auctions": auctions
    })

@login_required(login_url="login")
def comment(request, auction_id):
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return render(request, "auctions/auction.html", {
            "error": "This page does not exist.",
        })
    text = request.POST.get("text")
    if text:
        print("i am here")
        comment = Comment(user=request.user, auction=auction, text=text)
        comment.save()
    else:
        print(f"{text=}, nigga what?")
    return redirect("show_auction", auction_id)

def display_by_category(request):
    auctions = Auction.objects.all()

    if request.method == "POST":
        category = request.POST.get("category")
        auctions = auctions.filter(category=category)


    category_choices = Auction.CATEGORY_CHOICES
    return render(request, "auctions/display_by_category.html", {
        "auctions": auctions,
        "category_choices": category_choices,
    })