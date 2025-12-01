from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from recipes.models import Recipe

@login_required
def toggle_favourite(request):
    if request.method == "POST":
        recipe_id = request.POST.get("recipe_id")
        recipe = get_object_or_404(Recipe, id=recipe_id)

        # Check if the user already favourited it
        if request.user in recipe.favourites.all():
            recipe.favourites.remove(request.user)
            is_favourited = False
        else:
            recipe.favourites.add(request.user)
            is_favourited = True

        return JsonResponse({
            "is_favourited": is_favourited,
            "favourite_count": recipe.favourites.count(),
        })


@login_required
def favourite_list(request):
    favourites = request.user.favourite_recipes.all()

    return render(request, "recipes/favourite_list.html", {
        "favourites": favourites
    })