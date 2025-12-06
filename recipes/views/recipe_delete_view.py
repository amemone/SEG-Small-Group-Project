from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from recipes.models.recipes import Recipe
from django.views import View
from django.shortcuts import redirect


class RecipeDeleteView(View):
    def post(self, request):
        recipe_id = request.POST.get("recipe_id")
        recipe = Recipe.objects.get(id=recipe_id)

        if recipe.user == request.user:
            recipe.favourites.clear()
            recipe.delete()

        return redirect("dashboard")
