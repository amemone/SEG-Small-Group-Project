from django.test import TestCase
from recipes.models.user import User
from recipes.models.follow import Follow
from django.urls import reverse

class ProfileDisplayViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')
        self.third_user = User.objects.get(username='@petrapickles')
        self.url = reverse('view_profile')

    def test_view_profile_url(self):
        self.assertEqual(self.url, 'view_profile/')


    def test_following_count_starts_at_zero(self, user):
        self.assertEqual(Follow.objects.filter(follower=user).count(), 0)

    def test_following_count_is_1(self, user, second_user):
        user.follow(second_user)
        self.assertEqual(Follow.objects.filter(follower=user).count(), 1)

    def test_following_count_increases_more_than_once(self, user, second_user, third_user):
        user.follow(second_user)
        user.follow(third_user)
        self.assertEqual(Follow.objects.filter(follower=user).count(), 2)

    def test_follower_count_starts_at_0(self, user):
        self.assertEqual(Follow.objects.filter(followee=user).count(), 0)
    


    

