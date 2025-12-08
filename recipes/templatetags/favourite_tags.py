from django import template

register = template.Library()

@register.filter
def is_favourited(recipe, user):
    if not user.is_authenticated:
        return False
    return recipe.favourites.filter(id=user.id).exists()