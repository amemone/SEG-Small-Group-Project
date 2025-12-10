from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Exists, OuterRef, Count

from recipes.models.recipes import Recipe
from recipes.models.follow import Follow


@login_required
def feed_view(request):
    viewer = request.user
    sort = request.GET.get('sort', 'recent')
    recipes = Recipe.objects.all().select_related('user').prefetch_related('tags')

    owner_follows_viewer = Follow.objects.filter(
        follower=OuterRef('user'),
        followee=viewer
    )
    viewer_follows_owner = Follow.objects.filter(
        follower=viewer,
        followee=OuterRef('user')
    )

    recipes = recipes.annotate(
        owner_follows_viewer=Exists(owner_follows_viewer),
        viewer_follows_owner=Exists(viewer_follows_owner)
    ).filter(
        Q(visibility='public') |
        Q(visibility='friends',
          owner_follows_viewer=True,
          viewer_follows_owner=True) |
        Q(visibility='me', user=viewer)
    ).order_by('-publication_date')

    categories = ['Beginner', 'Intermediate', 'Advanced']
    selected_difficulty = request.GET.get('difficulty')
    if selected_difficulty in categories:
        recipes = recipes.filter(difficulty=selected_difficulty)

    # sort order
    if sort == "popular":
        recipes = recipes.annotate(
            fav_count=Count("favourite")   # adjust related name if different
        ).order_by("-fav_count", "-publication_date")
    else:
        recipes = recipes.order_by("-publication_date")

    context = {
        'recipes': recipes,
        'categories': categories,
        'selected_difficulty': selected_difficulty,
        'sort': sort,
    }
    return render(request, 'recipes/feed.html', context)
