from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.models.user import User
from recipes.models.follow import Follow

@login_required
def follow_user(request, username):
    try:
        followed_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("dashboard")

    if followed_user == request.user:
        messages.error(request, "Cannot follow yourself.")
        return redirect("dashboard")

    Follow.objects.get_or_create(follower=request.user, followee=followed_user)
    messages.success(request, f"You are now following {username}.")
    return redirect("dashboard")

@login_required
def unfollow_user(request, username):
    try:
        unfollowed_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("dashboard")

    if unfollowed_user == request.user:
        messages.error(request, "Cannot unfollow yourself.")
        return redirect("dashboard")

    Follow.objects.filter(follower=request.user, followee=unfollowed_user).delete()
    messages.success(request, f"You have unfollowed {username}")
    return redirect("dashboard")