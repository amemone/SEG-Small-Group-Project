from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.models.user import User
from recipes.models.follow import Follow
from django.shortcuts import render
from recipes.models.recipes import Recipe

@login_required
def follow(request):
    if request.method == 'GET' and 'username' in request.GET:
        username = request.GET.get('username')
        return redirect('follow_user', username=username)
    return render(request, 'follow.html')

@login_required
def follow_user(request, username):
    """
    Attempts to follow a user.

    Fails if the followed user does not exist, user tries to follow themselves,
    or if the user is already followed.
    """
    try:
        followed_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

    if followed_user == request.user:
        messages.error(request, "Cannot follow yourself.")
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

    if check_if_following(request.user, followed_user):
        messages.error(request, "You are already following this user.")
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

    Follow.objects.get_or_create(follower=request.user, followee=followed_user)
    messages.success(request, f"You are now following {username}.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

def check_if_following(follower, followee):
    """
    Checks if a user is following another user.

    Returns a boolean.
    """
    return Follow.objects.filter(follower=follower, followee=followee).exists()