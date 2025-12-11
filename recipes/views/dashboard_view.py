from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count
from recipes.models.recipes import Recipe
from datetime import timedelta
from recipes.helpers import paginate_recipes_user


@login_required
def dashboard(request):
    """
    Display the current user's dashboard.

    This view renders the dashboard page for the authenticated user.
    It ensures that only logged-in users can access the page. If a user
    is not authenticated, they are automatically redirected to the login
    page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered dashboard template with user data and their recipes.
    """

    current_user = request.user
    user_recipes = Recipe.objects.filter(
        user=current_user).order_by('-publication_date')
    recipes_page = paginate_recipes_user(
        request,
        viewer = current_user,
        profile_user = current_user
    )
    
    one_month_ago = timezone.now() - timedelta(days=30)

    popular_recipes = (
        Recipe.objects.filter(publication_date__gte=one_month_ago)
        .annotate(fav_count=Count("favourites"))
        .order_by("-fav_count", "-publication_date")[:12]
    )

    unread_count = request.user.notifications.filter(is_read=False).count()

    return render(request, 'dashboard.html', {
        'user': current_user,
        'recipes': user_recipes,
        'recipes_page': recipes_page,
        'show_delete': True,
        "popular_recipes": popular_recipes,
        "unread_count": unread_count,
    })
