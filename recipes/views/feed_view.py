from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Exists, OuterRef

from recipes.models.recipes import Recipe
from recipes.models.follow import Follow


@login_required
def feed_view(request):
    viewer = request.user
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

    context = {
        'recipes': recipes,
    }
    return render(request, 'recipes/feed.html', context)
