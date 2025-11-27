from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from recipes.models.follow import Follow


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["following"] = self.get_following_count(user)
        context["user_followings"] = self.get_following_users(user)
        context["followers"] = self.get_follower_count(user)
        context["user_followers"] = self.get_follower_users(user)
        context["user_name"] = user.username
        return context
