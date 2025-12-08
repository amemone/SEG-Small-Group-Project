"""Tests of the follow view."""
from django.contrib.messages import get_messages
from recipes.models.user import User
from recipes.models.follow import Follow
from django.test import TestCase
from django.urls import reverse

class FollowViewTestCase(TestCase):
    """Tests of the follow view."""

    #By default, @johndoe is following @janedoe.
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
        'recipes/tests/fixtures/default_follow.json'
    ]

    def setUp(self):
        self.follow_url = reverse('follow_user', args=['@janedoe'])
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')
        self.third_user = User.objects.get(username='@petrapickles')
        self.client.login(username='@johndoe', password="Password123")

    def _follow_and_check_response(self, username, message):
        response = self.client.get(reverse('follow_user', args=[username]))
        self.assertRedirects(response, reverse('dashboard'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_follow_url(self):
        self.assertEqual(self.follow_url, f'/follow/{self.second_user.username}/')

    def test_successful_follow(self):
        response_message = f"You are now following {self.third_user.username}."
        self._follow_and_check_response(self.third_user.username, response_message)
        self.assertTrue(Follow.objects.filter(follower=self.user, followee=self.third_user))
        self.assertEqual(Follow.objects.count(), 2)


    def test_follow_already_followed_user(self):
        response_message = "You are already following this user."
        self._follow_and_check_response(self.second_user.username, response_message)
        self.assertEqual(Follow.objects.count(), 1)

    def test_follow_user_that_doesnt_exist(self):
        response_message = "User not found."
        self._follow_and_check_response('@doesntexist', response_message)
        self.assertEqual(Follow.objects.count(), 1)

    def test_follow_yourself(self):
        response_message = "Cannot follow yourself."
        self._follow_and_check_response(self.user.username, response_message)
        self.assertEqual(Follow.objects.count(), 1)

    def test_follow_user_requires_login(self):
        self.client.logout()
        attempt_follow_url = reverse('follow_user', args=[self.third_user.username])
        response = self.client.get(attempt_follow_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/log_in/?next={attempt_follow_url}')