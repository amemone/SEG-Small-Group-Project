from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from recipes.models.recipes import Recipe


@login_required
def feed_view(request):
    # Quick test - does this show anything?
    # return HttpResponse("<h1>TEST - If you see this, the view works!</h1>")

    recipes = Recipe.objects.all().select_related(
        'user').order_by('-publication_date')
    print(f"\n=== DEBUG INFO ===")
    print(f"Found {recipes.count()} recipes")
    print(f"User: {request.user.username}")
    print(f"==================\n")

    context = {
        'recipes': recipes,
    }
    return render(request, 'recipes/feed.html', context)
