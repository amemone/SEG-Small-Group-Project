from django.shortcuts import render, get_object_or_404
from recipes.models.user import User
from recipes.helpers import (
    paginate_followers,
    paginate_following,
    get_following_count,
    get_follower_count,
    paginate_recipes_user,
    user_is_following
)

def user_profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        is_following = user_is_following(request.user, profile_user)
        recipes = paginate_recipes_user(request, request.user, profile_user)
    else:
        is_following = False
        recipes = paginate_recipes_user(request, None, profile_user)

    context = {
        'profile_user': profile_user,
        'following': get_following_count(profile_user),
        'user_followings': paginate_following(request, profile_user),
        'followers': get_follower_count(profile_user),
        'user_followers': paginate_followers(request, profile_user),
        'is_following': is_following,
        'recipes': recipes,
        'user_avatar': profile_user.gravatar(),

    }

    return render(request, 'user_profile.html', context)