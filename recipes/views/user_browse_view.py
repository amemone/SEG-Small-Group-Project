from django.shortcuts import render
from recipes.models.user import User
from django.db.models import Count
from django.core.paginator import Paginator

def user_browse_view(request):
    """
    Display a list of users based on a search query.
    """
    query = request.GET.get('q', '').strip()


    if not query:
        users = User.objects.none()
    else:
        users = User.objects.filter(username__icontains=query)

    top_users = get_top_followed_users(5)

    paginate = Paginator(users, 6)
    page_number = request.GET.get('page')
    page_object = paginate.get_page(page_number)

    return render(request, 'user_browse.html', {
        'users':users,
        'page_object': page_object,
        'top_users': top_users,
        'query':query,
        })

def get_top_followed_users(limit = 5):
    return (
        User.objects.annotate(follower_count=Count('followers', distinct=True))
        .order_by('-follower_count','username')[:limit]
    )