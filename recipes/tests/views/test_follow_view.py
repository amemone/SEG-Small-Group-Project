"""Tests of the follow view."""
from django.contrib import messages
from recipes.models.user import User
from recipes.models.follow import Follow
from django.test import TestCase
from django.urls import reverse

class FollowViewTestCase(TestCase):
    """Tests of the follow view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
        'recipes/tests/fixtures/default_follow.json'
    ]

    def setUp(self):
        self.follow_url = reverse('follow', args=['@janedoe'])
        self.unfollow_url = reverse('unfollow', args=['@janedoe'])
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')
        self.client.login(username='@johndoe', password="Password123")

    def test_follow_url(self):
        self.assertEqual(self.follow_url, f'/follow/{self.second_user.username}/')

    def test_unfollow_url(self):
        self.assertEqual(self.unfollow_url, f'/unfollow/{self.second_user.username}/')

    def test_successful_follow(self):
        response = self.client.get(reverse('follow', args=[self.second_user.username]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Follow.objects.filter(follower=self.user, followee=self.second_user))
