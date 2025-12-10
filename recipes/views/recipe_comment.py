# recipes/views/recipe_full_view.py

from django.shortcuts import redirect, get_object_or_404
from recipes.models import Recipe
from recipes.forms.comment_form import CommentForm
from django.contrib.auth.decorators import login_required

@login_required
def recipe_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.user = request.user
            comment.save()

    return redirect('view_recipe', pk=recipe_id)
