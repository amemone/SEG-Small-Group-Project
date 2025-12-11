"""
URL configuration for recipify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from recipes import views
from recipes.views.feed_view import feed_view
from recipes.views.follow_view import follow_user
from recipes.views.unfollow_view import unfollow_user
from recipes.views.recipe_create_view import recipe_create_view
from recipes.views.recipe_browse_view import recipe_browse_view
from recipes.views.user_browse_view import user_browse_view
from recipes.views.profile_display_view import profile_display_view
from recipes.views.favourite_view import toggle_favourite
from recipes.views.recipe_comment import recipe_comment
from recipes.views.mark_notification_read import mark_notification_read


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('feed/', feed_view, name='feed'),
    path('recipe/create/', recipe_create_view, name='recipe_create'),
    path('follow/<str:username>/', follow_user, name='follow_user'),
    path('unfollow/<str:username>/', unfollow_user, name='unfollow_user'),
    path('recipes/browse/', recipe_browse_view, name='recipe_browse'),
    path('recipes/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
    path('recipe/create/', recipe_create_view, name='recipe_create'),
    path('user_browse/', user_browse_view, name='user_browse'),
    path('view_profile/', profile_display_view, name='view_profile'),
    path("toggle_favourite/", toggle_favourite, name="toggle_favourite"),
    path('recipe/<int:pk>/',views.RecipeFullView.as_view(), name='view_recipe'),
    path('recipes/<int:recipe_id>/', recipe_comment, name='recipe_comment'),
    path('notification/<int:notification_id>/redirect/', mark_notification_read, name='notification_read'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
