from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from recipes.helpers import (
    get_following_count,
    get_following_users,
    get_follower_count,
    get_follower_users,
    paginate_following,
    paginate_followers,
    paginate_favourite_recipes,
)

@login_required
def profile_display_view(request):
    user = request.user
    context = {
        'following': get_following_count(user),
        'user_followings': paginate_following(request, user),
        'followers': get_follower_count(user),
        'user_followers': paginate_followers(request, user),
        'user_name': user.username,
        'favourites': paginate_favourite_recipes(request, user),
    }
    return render(request, 'view_profile.html', context)