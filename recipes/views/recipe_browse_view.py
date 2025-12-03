from django.shortcuts import render
from django.db.models import Q
from recipes.models.recipes import Recipe, Tag
from recipes.models.user import User
from recipes.models.follow import Follow   # <-- NEW IMPORT


def recipe_browse_view(request):
    """
    Display a list of recipes based on a search query
    """
    query = request.GET.get('q', '').strip()
    user = request.GET.get('user')
    date = request.GET.get('date')
    tags = request.GET.getlist('tag')

    recipes = Recipe.objects.all()
    users = User.objects.all()
    all_tags = Tag.objects.all()

    if not query and not tags and not user and not date:
        recipes = Recipe.objects.none()
    else:
        recipes = recipes.order_by('-publication_date')

        if query:
            recipes = recipes.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        if tags:
            recipes = recipes.filter(tags__name__in=tags).distinct()

        if user:
            recipes = recipes.filter(user__id=user)

        if date:
            recipes = recipes.filter(publication_date__date=date)

    viewer = request.user
    visible_recipes = []

    for recipe in recipes:
        owner = recipe.user

        if recipe.visibility == "public":
            visible_recipes.append(recipe)
            continue

        if recipe.visibility == "me":
            if viewer == owner:
                visible_recipes.append(recipe)
            continue

        if recipe.visibility == "friends":
            if viewer == owner:
                visible_recipes.append(recipe)
                continue

            viewer_follows_owner = Follow.objects.filter(
                follower=viewer, followee=owner
            ).exists()

            owner_follows_viewer = Follow.objects.filter(
                follower=owner, followee=viewer
            ).exists()

            if viewer_follows_owner and owner_follows_viewer:
                visible_recipes.append(recipe)

    return render(request, 'recipes/recipe_browse.html', {
        'recipes': visible_recipes,
        'query': query,
        'users': users,
        'tags': all_tags,
        'selected_tag': tags,
        'selected_user': user,
        'selected_date': date
    })
