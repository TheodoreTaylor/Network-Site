import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from network.forms import PostForm
from network.models import User, Post, Like, Follow
from network.utils import varified_user, paginate, users_liked_posts


def index(request):
    if request.method == "GET":
        # get user
        user = request.user.id

        # get user's posts
        post_list = Post.objects.all()

        # paginate posts
        posts = paginate(request, post_list)

        # get users liked posts - so that the correct options can be displayed for each post
        liked_posts = users_liked_posts(request)

        # render page
        return render(request, "network/index.html", {
            "posts": posts,
            "post_form": PostForm(initial={'user': user}),
            "liked_posts": liked_posts,
        })

    if request.method == "POST":
        # get post
        form = PostForm(request.POST)

        # check data, save to database, refresh/redirect to main index page
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))


@login_required
def following(request):
    # get liked posts
    liked_posts = users_liked_posts(request)

    # get users posts
    post_list = request.user.get_posts_by_users_followed()

    # paginate posts
    posts = paginate(request, post_list)

    # render page
    return render(request, "network/following.html", {
        "posts": posts,
        "liked_posts": liked_posts,
    })


def profile(request, user_id):
    # check is user is already followed and style "follow" button accordingly
    if Follow.objects.filter(user_id=user_id, follower=request.user.id):
        style = "text-decoration:line-through"
    else:
        style = ""

    # get user's liked posts
    liked_posts = users_liked_posts(request)

    # get posts made by profile owner
    post_list = Post.objects.filter(user_id=user_id)

    # paginate posts
    posts = paginate(request, post_list)

    # render page
    return render(request, "network/profile.html",
                  {"style": style, "posts": posts, "viewed_user": User.objects.get(id=user_id),
                   "liked_posts": liked_posts})


def like(request):
    """ function view - called by JS in order to apply likes/unlikes to the database """

    # get data from javascript request
    data = json.loads(request.body)

    # get user
    user = data["user"]

    # security check - stops fraudulent requests - e.g. logged in user doesn't match the user account being modified.
    if not varified_user(request, user):
        return JsonResponse({"status": "403"})
    else:
        # get data from request
        post = data["post"]

        # check if like already exists
        existing_like = Like.objects.filter(related_user_id=user, post_id=post)

        # if like exists, remove it and send json confirmation, updating the total number of likes
        if existing_like:
            # remove existing record
            existing_like.delete()

            # get updated number of likes
            number_of_likes = Like.objects.filter(post_id=post).count()

            # return confirmation and total likes
            return JsonResponse({"status":  "200", "text": "[like]", "likes": number_of_likes})
        else:
            # if like doesnt exist, add it and send json confirmation, updating the total number of likes

            # make new record
            new_like = Like(related_user_id=user, post_id=post)

            # add to database
            new_like.save()

            # get updated number of likes
            number_of_likes = Like.objects.filter(post_id=post).count()

            # return confirmation and total likes
            return JsonResponse({"status": "200", "text": "[<strike>like</strike>]", "likes": number_of_likes})


def follow(request):
    # get data from request
    data = json.loads(request.body)
    user = data["user"]
    follower = data["follower"]

    # security check - stops fraudulent requests - e.g. logged in user doesn't match the user account being modified.
    if not varified_user(request, follower):
        return JsonResponse({"status": "403"})
    else:
        # check if requester already follows user profile
        follows = Follow.objects.filter(user_id=user, follower_id=follower)

        """ If follows, remove follow record and send updated details in json """
        if follows:
            # remove existing record
            follows.delete()

            # get updated number of followers
            followers = Follow.objects.filter(user_id=user).count()

            # return confirmation and total followers
            return JsonResponse({"status": "200", "strike": False, "followers": followers})
        else:
            """ If not, add follow record and send updated details in json """

            # create new record
            new_follow = Follow(user_id=user, follower_id=follower)

            # save to database
            new_follow.save()

            # get total followers
            followers = Follow.objects.filter(user_id=user).count()

            # return confirmation and total followers
            return JsonResponse({"status": "200", "strike": True, "followers": followers})


def edit(request):
    # get data from request
    data = json.loads(request.body)

    # find post in database
    p = Post.objects.get(id=data["post"])

    # security check - stops fraudulent requests - e.g. logged in user doesn't match the user account being modified.
    if not varified_user(request, p.user_id):
        return JsonResponse({"status": "403"})
    else:
        # get new content from request
        new = data["new_content"]

        # update content of post in database
        p.content = new

        # save the post
        p.save()

        # get time of latest update
        created_updated = p.created_or_modified()

        # return confirmation and latest update time
        return JsonResponse({"status": "200", "created_updated": created_updated})


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
