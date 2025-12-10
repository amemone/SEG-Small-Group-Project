### Helper function and classes go here.
from django.core.paginator import Paginator
from recipes.models.follow import Follow
from recipes.models.recipes import Recipe

def get_following_count(user):
    return Follow.objects.filter(follower=user).count()

def get_following_users(user):
    followings = Follow.objects.filter(follower=user).select_related('followee')
    return [following_user.followee for following_user in followings]

def get_follower_count(user):
    return Follow.objects.filter(followee=user).count()

def get_follower_users(user):
    followers = Follow.objects.filter(followee=user).select_related('follower')
    return [follower_user.follower for follower_user in followers]

def paginate_following(request,user):
    followings = get_following_users(user)
    following_paginate = Paginator(followings, 5)
    page_number = request.GET.get('following_page')
    page_object = following_paginate.get_page(page_number)
    return page_object
    
def paginate_followers(request,user):
    followers = get_follower_users(user)
    follower_paginate = Paginator(followers, 5)
    page_number = request.GET.get('follower_page')
    page_object = follower_paginate.get_page(page_number)
    return page_object

def user_is_following(viewer, profile_user):
    return Follow.objects.filter(
        follower=viewer,
        followee=profile_user
    ).exists()

def paginate_favourite_recipes(request, user):
    favourites_recipes = (
        Recipe.objects
        .filter(favourite__user=user)
        .order_by('-favourite__favourited_at')
    )
    favourite_paginate = Paginator(favourites_recipes, 9)
    page_number = request.GET.get('page')
    return favourite_paginate.get_page(page_number)


def paginate_recipes_user(request, viewer, profile_user):
    if viewer == profile_user:
        recipes = Recipe.objects.filter(user=profile_user)
    else:
        is_following = user_is_following(viewer, profile_user)
        if is_following:
            recipes = Recipe.objects.filter(user=profile_user)
        else:
            recipes = Recipe.objects.filter(user=profile_user, visibility="public")
    recipes = recipes.order_by('-publication_date')
    recipes_paginate = Paginator(recipes, 9)
    page_number = request.GET.get('page')
    return recipes_paginate.get_page(page_number)
