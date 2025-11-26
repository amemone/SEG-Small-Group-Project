from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.models.user import User
from recipes.models.follow import Follow
from django.shortcuts import render
from recipes.models.recipes import Recipe

@login_required
def unfollow_user(request, username):
    """
    Attempts to unfollow a user.

    Fails if the unfollowed user does not exist, user tries to unfollow themselves,
    or if user is already not followed.
    """
    try:
        unfollowed_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("dashboard")

    if unfollowed_user == request.user:
        messages.error(request, "Cannot unfollow yourself.")
        return redirect("dashboard")

    if check_if_following(request.user, unfollowed_user):
        Follow.objects.filter(follower=request.user, followee=unfollowed_user).delete()
        messages.success(request, f"You have unfollowed {username}.")
        return redirect("dashboard")

    messages.error(request, f"You are not following {username}.")
    return redirect("dashboard")

def check_if_following(follower, followee):
    """
    Checks if a user is following another user.

    Returns a boolean.
    """
    return Follow.objects.filter(follower=follower, followee=followee).exists()