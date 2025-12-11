from django.shortcuts import render
from django.db.models import Q, Count
from recipes.models.recipes import Recipe, Tag
from recipes.models.user import User


def recipe_browse_view(request):
    """
    Display a list of recipes based on a search query
    """
    query = request.GET.get('q', '').strip()
    user_id = request.GET.get('user')  # get user from GET
    date = request.GET.get('date')
    tags = request.GET.getlist('tag')
    category = request.GET.get('category')
    popular = request.GET.get('popular')
    time_required = request.GET.get('time')
    
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
    else:
        unread_count = 0

    if user_id:
        user_id = int(user_id)  # convert to integer for comparison in template

    recipes = Recipe.objects.all()
    users = User.objects.all()
    all_tags = Tag.objects.all()
    categories = [choice[0] for choice in Recipe.DIFFICULTY_CHOICES]

    if not query and not tags and not user_id and not date and not category and not time_required:
        recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).order_by('-publication_date')

    if tags:
        recipes = recipes.filter(tags__name__in=tags).distinct()

    if user_id:
        recipes = recipes.filter(user__id=user_id)

    if date:
        recipes = recipes.filter(publication_date__date=date)

    if category:
        recipes = recipes.filter(difficulty=category)
    
    if time_required:
        recipes = recipes.filter(time_required=time_required)
        
    if popular:
        recipes = filter_by_popularity(recipes)
    

    selected_difficulty = request.GET.get('difficulty')
    if selected_difficulty in [choice[0] for choice in Recipe.DIFFICULTY_CHOICES]:
        recipes = recipes.filter(difficulty=selected_difficulty)

    return render(request, 'recipes/recipe_browse.html', {
        'recipes': recipes,
        'query': query,
        'users': users,
        'tags': all_tags,
        'categories': categories,
        'selected_tags': tags,
        'selected_user': user_id,
        'selected_date': date,
        'selected_time': time_required,
        'selected_difficulty': selected_difficulty,
        "unread_count": unread_count,
        'popular' : popular
    })

def filter_by_popularity(queryset):
    queryset = queryset.annotate(favourite_count=Count('favourites'))
    return queryset.order_by('-favourite_count', '-publication_date')
