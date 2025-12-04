from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from recipes.models.follow import Follow
from recipes.models import Recipe


class ProfileDisplayView(LoginRequiredMixin, TemplateView):
    template_name = "view_profile.html"

    def get_following_count(self, user):
        return Follow.objects.filter(follower=user).count()

    def get_following_users(self, user):
        following_users = Follow.objects.filter(follower=user).select_related("followee")
        return [following_user.followee for following_user in following_users]

    def get_follower_count(self, user):
        return Follow.objects.filter(followee=user).count()

    def get_follower_users(self, user):
        follower_users = Follow.objects.filter(followee=user).select_related("follower")
        return [follower_user.follower for follower_user in follower_users]
    
    def get_favourites_user(self, user):
        favourites_recipes = (
            Recipe.objects
            .filter(favourite__user=user)
            .order_by("-favourite__favourited_at") 
        )
        paginator = Paginator(favourites_recipes, 12) 
        current_page_number = self.request.GET.get("page")
        return paginator.get_page(current_page_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["following"] = self.get_following_count(user)
        context["user_followings"] = self.get_following_users(user)
        context["followers"] = self.get_follower_count(user)
        context["user_followers"] = self.get_follower_users(user)
        context["user_name"] = user.username
        context["favourites"] = self.get_favourites_user(user)
        return context
