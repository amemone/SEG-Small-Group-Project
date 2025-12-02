from django.test import TestCase
from recipes.models.user import User
from recipes.models.follow import Follow
from django.urls import reverse

class ProfileDisplayViewTest(TestCase):

    def setUp(self):
        """Test of the profile display view """
        self.user = User.objects.create_user(
            username='@johndoe',
            email='john@example.com',
            password='Password123',
            first_name='John',
            last_name='Doe',
        )
        self.second_user = User.objects.create_user(
            username='@janedoe',
            email='jane@example.com',
            password='Password123',
            first_name='Jane',
            last_name='Doe',
        )
        self.third_user = User.objects.create_user(
            username='@petrapickles',
            email='petra@example.com',
            password='Password123',
            first_name='Petra',
            last_name='Pickles',
        )
        self.url = reverse('view_profile')
        self.client.login(username='@johndoe', password="Password123")

    def test_view_profile_url(self):
        self.assertEqual(self.url, '/view_profile/')

    def test_following_count_starts_at_zero(self):
        following_count = Follow.objects.filter(follower = self.user).count()
        self.assertEqual(following_count, 0)

    def test_follower_count_starts_at_zero(self):
        follower_count = Follow.objects.filter(followee = self.user).count()
        self.assertEqual(follower_count, 0)

    def test_profile_view_shows_no_followers_or_following_initially(self):
        response = self.client.get(reverse('view_profile'))
        self.assertEqual(response.status_code,200)

        self.assertEqual(response.context["following"], 0)
        self.assertEqual(response.context["followers"], 0)

        self.assertEqual(list(response.context["user_followings"]), [])
        self.assertEqual(list(response.context["user_followers"]), [])
        
        self.assertContains(response, "<b>No Users</b>", html=True)

    def test_following_count_increases_when_following_someone(self):
        initial_count = Follow.objects.filter(follower = self.user).count()
        Follow.objects.create(follower = self.user, followee = self.second_user)
        new_count = Follow.objects.filter(follower = self.user).count()
        self.assertEqual(new_count, initial_count + 1)

    def test_follower_count_increases_when_getting_followed(self):
        initial_count = Follow.objects.filter(followee = self.second_user).count()
        Follow.objects.create(follower = self.user, followee = self.second_user)
        new_count = Follow.objects.filter(followee = self.second_user).count()
        self.assertEqual(new_count, initial_count + 1)

    def test_following_users_contains_and_excludes_expected_users(self):
        Follow.objects.get_or_create(follower = self.user, followee = self.second_user)
        Follow.objects.get_or_create(follower = self.user, followee = self.third_user)
        following_users = [
            user.followee.username
            for user in
            Follow.objects.filter(follower = self.user).select_related('followee')
        ]
        self.assertIn(self.second_user.username, following_users)
        self.assertIn(self.third_user.username, following_users)

    def test_unfollow_decreases_following_count_and_removes_user(self):
        follow_relationship = Follow.objects.filter(follower=self.user, followee=self.second_user).first()
        if follow_relationship is None:
            follow_relationship = Follow.objects.create(follower = self.user, followee = self.second_user)
        
        initial_count = Follow.objects.filter(follower = self.user).count()

        #unfollow
        follow_relationship.delete()
        new_count = Follow.objects.filter(follower = self.user).count()
        self.assertEqual(new_count, initial_count - 1)
        self.assertFalse(Follow.objects.filter(follower = self.user, followee= self.second_user).exists())

