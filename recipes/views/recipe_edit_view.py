from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseForbidden
from django.views import View

from recipes.models.recipes import Recipe
from recipes.forms import RecipeForm


class RecipeEditView(View):
    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if recipe.user != request.user:
            return HttpResponseForbidden("You are not allowed to edit this recipe.")

        form = RecipeForm(instance=recipe)
        return render(request, "recipes/recipe_edit.html", {"form": form, "recipe": recipe})

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if recipe.user != request.user:
            return HttpResponseForbidden("You are not allowed to edit this recipe.")

        form = RecipeForm(request.POST, instance=recipe)

        if form.is_valid():
            form.save()
            # redirect back to the recipe page
            return redirect("view_recipe", recipe.id)

        # Use the same template as GET
        return render(request, "recipes/recipe_edit.html", {"form": form, "recipe": recipe})
