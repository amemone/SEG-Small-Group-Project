from django.shortcuts import render
from django.db.models import Q
from recipes.models.recipes import Recipe, Tag
from recipes.models.user import User


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
        if query:
            recipes = Recipe.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        if tags:
            recipes = Recipe.objects.filter(tags__name__in=tags).distinct()
        if user:
           recipes = Recipe.objects.filter(user__id=user)

        if date:
            recipes = Recipe.objects.filter(publication_date__date=date)

    return render(request, 'recipes/recipe_browse.html', {
<< << << < HEAD
        'recipes': recipes,
        'query': query
    })


== == == =
        'recipes': recipes.order_by('-publication_date'),
        'query': query,
        'users': users,
        'tags': all_tags,
        'selected_tag': tags,
        'selected_user': user,
        'selected_date': date
    })
>>>>>>> e19aaf80478270abea3a4446ea2e6b9103f8a709
