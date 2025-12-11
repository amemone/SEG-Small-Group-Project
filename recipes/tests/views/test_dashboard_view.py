from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe

class DashboardViewTest(TestCase):

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        """Tests for the dashboard view"""
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')
        self.url = reverse('dashboard')
        self.client.login(username='@johndoe', password="Password123")

    def test_dashboard_url(self):
        self.assertEqual(self.url, '/dashboard/')

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/log_in" in response.url)

    def test_dashboard_loads_successfully(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('recipes_page', response.context)

    def test_dashboard_initially_has_no_recipes(self):
        response = self.client.get(self.url)
        recipes_page = response.context["recipes_page"]
        self.assertEqual(list(recipes_page.object_list), [])
        self.assertContains(response, "You haven't created any recipes yet.")

    def test_dashboard_lists_recipes(self):
        first_recipe = Recipe.objects.create(
            title="Grilled Cheese",
            description="Bread, cheese",
            user=self.user
        )
        second_recipe = Recipe.objects.create(
            title="Cereal",
            description="Cereal, milk",
            user=self.user
        )
        response = self.client.get(self.url)
        recipes_page = response.context["recipes_page"]
        recipe_list = list(recipes_page.object_list)
        self.assertIn(first_recipe, recipe_list)
        self.assertIn(second_recipe, recipe_list)

    def test_dashboard_pagination_page_size(self):
        for i in range(12):
            Recipe.objects.create(
                title=f"Recipe {i}",
                description="test",
                user=self.user
            )

        response = self.client.get(self.url + "?page=1")
        first_page = response.context["recipes_page"]
        self.assertEqual(len(first_page.object_list), 9)
        self.assertTrue(first_page.has_next())
        response = self.client.get(self.url + "?page=2")
        second_page = response.context["recipes_page"]
        self.assertEqual(len(second_page.object_list), 3)
        self.assertFalse(second_page.has_next())

    def test_dashboard_invalid_page_returns_last_page(self):
        for i in range(5):
            Recipe.objects.create(
                title=f"Recipe {i}",
                description="test",
                user=self.user
            )
        response = self.client.get(self.url + "?page=999")
        recipes_page = response.context["recipes_page"]
        self.assertEqual(
            recipes_page.number,
            recipes_page.paginator.num_pages
        )

    def test_dashboard_search_with_pagination(self):
        for i in range(12):
            Recipe.objects.create(
                title=f"Test recipe {i}",
                description="test",
                user=self.user
            )

        response = self.client.get(self.url + "?search=chocolate&page=1")
        first_page = response.context["recipes_page"]
        self.assertEqual(len(first_page.object_list), 9)
        self.assertTrue(first_page.has_next())
        response = self.client.get(self.url + "?search=chocolate&page=2")
        second_page = response.context["recipes_page"]
        self.assertEqual(len(second_page.object_list), 3)
        self.assertFalse(second_page.has_next())