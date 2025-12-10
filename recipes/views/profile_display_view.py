from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from recipes.models.follow import Follow
from recipes.models import Recipe

def get_following_count(user):
    return Follow.objects.filter(follower=user).count()

def get_following_users(user):
    following_users = Follow.objects.filter(follower=user).select_related('followee')
    return [following_user.followee for following_user in following_users]

def get_follower_count(user):
        return Follow.objects.filter(followee=user).count()

def get_follower_users(user):
    follower_users = Follow.objects.filter(followee=user).select_related('follower')
    return [follower_user.follower for follower_user in follower_users]
    
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
    
def get_favourites_user(request, user):
    favourites_recipes = (
        Recipe.objects
        .filter(favourite__user=user)
        .order_by('-favourite__favourited_at') 
    )
    paginator = Paginator(favourites_recipes, 12) 
    current_page_number = request.GET.get('page')
    return paginator.get_page(current_page_number)

@login_required
def profile_display_view(request):
    user = request.user
    context = {
         'following': get_following_count(user),
         'user_followings': paginate_following(request, user),
         'followers': get_follower_count(user),
         'user_followers': paginate_followers(request, user),
         'user_name': user.username,
         'user_avatar': user.gravatar(),
         'favourites': get_favourites_user(request, user)
    }
    return render(request, 'view_profile.html',context)
    
