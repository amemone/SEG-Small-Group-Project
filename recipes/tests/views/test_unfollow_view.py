"""Tests of the unfollow view."""
from django.contrib.messages import get_messages
from recipes.models.user import User
from recipes.models.follow import Follow
from django.test import TestCase
from django.urls import reverse

class FollowViewTestCase(TestCase):
    """Tests of the unfollow view."""

    #By default, @johndoe is following @janedoe.
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
        'recipes/tests/fixtures/default_follow.json'
    ]

    def setUp(self):
        self.unfollow_url = reverse('unfollow', args=['@janedoe'])
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')
        self.third_user = User.objects.get(username='@petrapickles')
        self.client.login(username='@johndoe', password="Password123")

    def _unfollow_and_check_response(self, username, message):
        response = self.client.get(reverse('unfollow', args=[username]))
        self.assertRedirects(response, reverse('dashboard'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), message)

    def test_unfollow_url(self):
        self.assertEqual(self.unfollow_url, f'/unfollow/{self.second_user.username}/')

    def test_successful_unfollow(self):
        response_message = f"You have unfollowed {self.second_user.username}."
        self._unfollow_and_check_response(self.second_user.username, response_message)
        self.assertEqual(Follow.objects.count(), 0)

    def test_unfollow_already_unfollowed_user(self):
        response_message = f"You are not following {self.third_user.username}."
        self._unfollow_and_check_response(self.third_user.username, response_message)
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow_user_that_doesnt_exist(self):
        response_message = f"User not found."
        self._unfollow_and_check_response('@doesntexist', response_message)
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow_self(self):
        response_message = "Cannot unfollow yourself."
        self._unfollow_and_check_response(self.user.username, response_message)
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow_user_requires_login(self):
        self.client.logout()
        attempt_unfollow_url = reverse('unfollow', args=[self.third_user.username])
        response = self.client.get(attempt_unfollow_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/log_in/?next={attempt_unfollow_url}')