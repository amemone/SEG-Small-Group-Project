from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe, Comment, Notification


class RecipeCommentViewTestCase(TestCase):
    """Tests for the recipe_comment view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.create_user(username='@janedoe', password='Password123')
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test description',
            user=self.other_user
        )
        self.comment_url = reverse('recipe_comment', kwargs={'recipe_id': self.recipe.id})
        self.view_url = reverse('view_recipe', kwargs={'pk': self.recipe.id})

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(self.comment_url, {'text': 'Nice recipe!'})
        login_url = reverse('log_in') + f"?next={self.comment_url}"
        self.assertRedirects(response, login_url)

    def test_valid_comment_creates_comment(self):
        self.client.force_login(self.user)
        response = self.client.post(self.comment_url, {'text': 'Nice recipe!'})
        self.assertRedirects(response, self.view_url)
        comment = Comment.objects.get(recipe=self.recipe, user=self.user)
        self.assertEqual(comment.text, 'Nice recipe!')

    def test_notification_created_for_other_user(self):
        self.client.force_login(self.user)
        self.client.post(self.comment_url, {'text': 'Great!'})
        notification = Notification.objects.get(user=self.other_user)
        expected_text = f"{self.user.username} commented on your recipe '{self.recipe.title}'"
        self.assertEqual(notification.text, expected_text)
        self.assertEqual(notification.link, f"/recipe/{self.recipe.id}/")

    def test_no_notification_when_commenting_on_own_recipe(self):
        self.client.force_login(self.user)
        own_recipe = Recipe.objects.create(title='My Recipe', description='Test', user=self.user)
        url = reverse('recipe_comment', kwargs={'recipe_id': own_recipe.id})
        self.client.post(url, {'text': 'Self comment'})
        self.assertFalse(Notification.objects.filter(user=self.user, text__contains='Self comment').exists())

    def test_invalid_form_does_not_create_comment(self):
        self.client.force_login(self.user)
        response = self.client.post(self.comment_url, {'text': ''})  # blank text
        self.assertRedirects(response, self.view_url)
        self.assertFalse(Comment.objects.filter(recipe=self.recipe, user=self.user).exists())
