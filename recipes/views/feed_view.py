from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from recipes.models.recipes import Recipe


@login_required
def feed_view(request):
    print("ALL RECIPES IN DATABASE:")
    for r in Recipe.objects.all():
        print(r.title, "| user:", r.user.username)
    recipes = Recipe.objects.all().order_by('-publication_date')
    context = {
        'recipes': recipes,
    }
    return render(request, 'recipes/feed.html', context)
