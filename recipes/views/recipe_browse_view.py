from django.shortcuts import render
from django.db.models import Q
from recipes.models.recipes import Recipe, Tag
from recipes.models.user import User


def recipe_browse_view(request):
    """
    Display a list of recipes based on a search query
    """
    query = request.GET.get('q', '').strip()
    user_id = request.GET.get('user')  # get user from GET
    date = request.GET.get('date')
    tags = request.GET.getlist('tag')

    if user_id:
        user_id = int(user_id)  # convert to integer for comparison in template

    recipes = Recipe.objects.all()
    users = User.objects.all()
    all_tags = Tag.objects.all()

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if tags:
        recipes = recipes.filter(tags__name__in=tags).distinct()

    if user_id:
        recipes = recipes.filter(user__id=user_id)

    if date:
        recipes = recipes.filter(publication_date__date=date)

    # Order by newest first
    recipes = recipes.order_by('-publication_date')

    return render(request, 'recipes/recipe_browse.html', {
        'recipes': recipes,
        'query': query,
        'users': users,
        'tags': all_tags,
        'selected_tags': tags,
        'selected_user': user_id,
        'selected_date': date
    })
