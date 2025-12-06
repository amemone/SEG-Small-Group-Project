from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe, Favourite
from recipes.tests.helpers import reverse_with_next


class FavouriteViewTest(TestCase):
    """Tests of the favourite view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            title="Yoghurt bowl",
            description="Greek yoghurt, granola, banana",
            user=self.user
        )
        self.toggle_url = reverse('toggle_favourite')

    def test_toggle_favourite_url(self):
        self.assertEqual(self.toggle_url, '/toggle_favourite/')

    def test_toggle_favourite_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.toggle_url)
        response = self.client.post(self.toggle_url, {"recipe_id": self.recipe.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_can_favourite_recipe(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.toggle_url, {"recipe_id": self.recipe.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_favourited"])
        self.assertEqual(data["favourite_count"], 1)
        self.assertTrue(
            Favourite.objects.filter(user=self.user, recipe=self.recipe).exists()
        )

    def test_can_unfavourite_recipe(self):
        Favourite.objects.create(user=self.user, recipe=self.recipe)
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.toggle_url, {"recipe_id": self.recipe.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_favourited"])
        self.assertEqual(data["favourite_count"], 0)
        self.assertFalse(
            Favourite.objects.filter(user=self.user, recipe=self.recipe).exists()
        )