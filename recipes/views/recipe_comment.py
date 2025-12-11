from django.shortcuts import redirect, get_object_or_404
from recipes.models import Recipe
from recipes.models.comment import Notification
from recipes.forms.comment_form import CommentForm
from django.contrib.auth.decorators import login_required

@login_required
def recipe_comment(request, recipe_id):
    """
    Allows the user to comment on recipes
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.user = request.user
            comment.save()

            # Create notification if not commenting on your own recipe
            if recipe.user != request.user:
                Notification.objects.create(
                    user=recipe.user,
                    text=f"{request.user.username} commented on your recipe '{recipe.title}'",
                    link=f"/recipe/{recipe.id}/"
                )

    return redirect('view_recipe', pk=recipe_id)
    

    
