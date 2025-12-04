from django.views.generic import DetailView
from recipes.models.recipes import Recipe


class RecipeFullView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_full.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'recipe'

    def get_object(self):
        recipe = super().get_object()
        return recipe
