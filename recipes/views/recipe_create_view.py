from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.forms.recipe_form import RecipeForm  # Changed from recepy_form


@login_required
def recipe_create_view(request):
    """
    Handle recipe creation for authenticated users.
    """
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            form.save_m2m() 
            messages.success(request, 'Recipe created successfully!')
            return redirect('feed')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecipeForm()

    return render(request, 'recipes/recipe_form.html', {'form': form})
