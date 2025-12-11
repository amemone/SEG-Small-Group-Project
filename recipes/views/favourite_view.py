from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from recipes.models import Recipe, Favourite
from recipes.models.comment import Notification

@login_required
def toggle_favourite(request):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, id=request.POST.get("recipe_id"))
        favourite, favourite_was_created = Favourite.objects.get_or_create(
            recipe=recipe,
            user=request.user
        )
        if favourite_was_created:
            is_favourited = True
        else:
            favourite.delete()
            is_favourited = False

        if recipe.user != request.user:
                Notification.objects.create(
                    user=recipe.user,
                    text=f"{request.user.username} favourited your recipe '{recipe.title}'",
                    link=f"/recipe/{recipe.id}/"
                )

        return JsonResponse({
            "is_favourited": is_favourited,
            "favourite_count": Favourite.objects.filter(recipe=recipe).count(),
        })