from django.shortcuts import render
from django.db.models import Q
from recipes.models.recipes import Recipe

def recipe_browse_view(request):
    """
    Display a list of recipes based on a search query
    """
    query = request.GET.get('q','')

    query = query.strip()

    if query:
        recipes = Recipe.objects.filter(
            Q(title__icontains = query) |
            Q(description__icontains = query)
        ).order_by('-publication_date').distinct()
    else:
        recipes = Recipe.objects.none()

    return render(request, 'recipes/recipe_browse.html', {
        'recipes': recipes,
        'query': query
    })