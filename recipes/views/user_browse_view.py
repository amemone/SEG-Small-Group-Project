from django.shortcuts import render
from recipes.models.user import User

def user_browse_view(request):
    """
    Display a list of users based on a search query.
    """
    query = request.GET.get('q', '').strip()


    if not query:
        users = User.objects.none()
    else:
        users = User.objects.filter(username__icontains=query)

    return render(request, 'user_browse.html', {'users': users})