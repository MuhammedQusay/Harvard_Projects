from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.core.paginator import Paginator
from django.core.validators import URLValidator

from .models import Post, User, Comment


def clean_input(text):
    # Normalize multiple blank lines to a single blank line
    import re
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

def pagination_range(total_pages, current_page):
    if total_pages <= 5:
        return range(1, total_pages + 1)
    else:
        if current_page <= 3:
            return range(1, 6)
        elif current_page >= total_pages - 2:
            return range(total_pages - 4, total_pages + 1)
        else:
            return range(current_page - 2, current_page + 3)


def index(request):

    if request.method == "POST":
        if request.user.is_authenticated:
            content = request.POST.get("content").strip()

            content = clean_input(content)

            post = Post(poster=request.user, content=content)
            post.save()
        else:
            return redirect("login")

    all_posts = Post.objects.order_by("-timestamp")

    paginator = Paginator(all_posts, 10)
    page_num = request.GET.get("page", 1)
    page_objects = paginator.get_page(page_num)

    page_rage = pagination_range(paginator.num_pages, page_objects.number)

    return render(request, "network/index.html", {
        "posts" : page_objects,
        "page_range" : page_rage,
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile_view(request, user_id):
    try:
        poster = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse()

    posts = Post.objects.filter(poster=poster).order_by('-timestamp')

    paginator = Paginator(posts, 10)
    page_num = request.GET.get("page")
    page_objects = paginator.get_page(page_num)

    page_range = pagination_range(paginator.num_pages, page_objects.number)


    if request.user in poster.followers.all():
        is_following = "true"
    else:
        is_following = "false"

    return render(request, "network/profile_view.html", {
        "poster" : poster,
        "posts" : page_objects,
        "is_following" : is_following,
        "page_range" : page_range,
    })



def post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse()

    comments = post.comments.order_by("timestamp")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        comment_text = request.POST.get("comment_text").strip()
        if comment_text:
            Comment.objects.create(
                post=post,
                commenter=request.user,
                text=comment_text
            )
            return redirect("post_detail", post_id)

    return render(request, "network/post_detail.html", {
        "post": post,
        "comments": comments
    })


@login_required(login_url="login")
def following_view(request):
    if request.method == "POST":
        content = request.POST.get("content").strip()

        post = Post(poster=request.user, content=content)
        post.save()

    posts = Post.objects.filter(poster__in=request.user.following.all()).order_by('-timestamp')

    paginator = Paginator(posts, 10)
    page_num = request.GET.get("page")
    page_objects = paginator.get_page(page_num)


    page_rage = pagination_range(paginator.num_pages, page_objects.number)

    return render(request, "network/index.html", {
        "posts" : page_objects,
        "page_range" : page_rage,
    })


@login_required(login_url="login")
@csrf_exempt
def toggle_like(request, post_id):

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse()

    if request.method == "POST":
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        return JsonResponse({
            "liked": liked,
            "likes_count": post.likes.count(),
        })
    else:
        return JsonResponse({"error": "POST method required"}, status=400)

@csrf_exempt
@login_required(login_url="login")
def toggle_follow(request, user_id):

    try:
        user_to_follow = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse()

    if request.user in user_to_follow.followers.all():
        user_to_follow.followers.remove(request.user)
        return JsonResponse({"Success":"User Ufollowed"})
    else:
        user_to_follow.followers.add(request.user)
        return JsonResponse({"Success":"User Followed"})


@csrf_exempt
@login_required(login_url="login")
def edit_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse()

    if request.user != post.poster:
        return JsonResponse({"error": "You are not authorized to edit this post."})
    try:
        data = json.loads(request.body)
        content = clean_input(data.get("content", "").strip())
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    if not content:
        return JsonResponse({"error": "Content cannot be empty."}, status=400)

    post.content = content
    post.save()

    return JsonResponse({"content": post.content})


@csrf_exempt
@login_required(login_url="login")
def edit_profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse()


    if request.user != user:
        return JsonResponse({"error": "You are not authorized to edit this bio."})

    try:
        data = json.loads(request.body)
        new_bio = clean_input(data.get("new_bio", "").strip())
        new_pic = data.get("new_pic", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    validator = URLValidator()
    try:
        validator(new_pic)
    except:
        new_pic = "https://openclipart.org/image/400px/346569"


    user.bio = new_bio
    user.profile_picture = new_pic
    user.save()

    return JsonResponse({"new_bio": user.bio})
