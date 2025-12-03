# recipes/views/recipe_detail_view.py
from django.views.generic import DetailView
from recipes.models.recipes import Recipe


class RecipeFullView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_full.html'
    context_object_name = 'recipe'
