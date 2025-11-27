"""Unit tests for the Follow model."""
from socket import send_fds

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from recipes.models import User
from recipes.models import Follow

class FollowModelTestCase(TestCase):
    """Unit tests for the Follow model."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
        'recipes/tests/fixtures/default_follow.json'
    ]

    def setUp(self):
        self.follow = Follow.objects.get(follower=1)
        self.user = User.objects.get(username='@johndoe')

    def test_valid_follow(self):
        self.follow.full_clean()

    def test_cannot_have_multiple_same_follow_relation(self):
        self.second_user = User.objects.get(username='@janedoe')
        with self.assertRaises(IntegrityError):
            self.duplicate_follow = Follow.objects.create(follower=self.user, followee=self.second_user)
            self.follow.full_clean()
            self.duplicate_follow.full_clean()