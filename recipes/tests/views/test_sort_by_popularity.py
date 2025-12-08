from django.test import TestCase
from recipes.models import User, Favourite
from django.urls import reverse
from recipes.models.recipes import Recipe

class SortByPopuarityTest(TestCase):
    """Test Suite for sorting recipes by popularity"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='@user1',
            email='user1@example.com',
            password='Password123',
            first_name='User',
            last_name='One',
        )
        self.user2 = User.objects.create_user(
            username='@user2',
            email='user2@example.com',
            password='Password123',
            first_name='User',
            last_name='Two',
        )
        self.user3 = User.objects.create_user(
            username='@user3',
            email='user3@example.com',
            password='Password123',
            first_name='User',
            last_name='Three',
        )
        self.recipe1 = Recipe.objects.create(
            title='Recipe 1',
            description='desc',
            user=self.user1,
        )
        self.recipe2 = Recipe.objects.create(
            title='Recipe 2',
            description='desc',
            user=self.user1,
        )
        self.recipe3 = Recipe.objects.create(
            title='Recipe 3',
            description='desc',
            user=self.user1,
        )
        self.browse_url = reverse('recipe_browse')

    def test_most_favourited_recipe_appears_first_when_sorted_by_popularity(self):
        recipe1 = Recipe.objects.create(
            title='Recipe 1',
            description='desc',
            user=self.user1,
        )
        recipe2 = Recipe.objects.create(
            title='Recipe 2',
            description='desc',
            user=self.user1,
        )
        recipe3 = Recipe.objects.create(
            title='Recipe 3',
            description='desc',
            user=self.user1,
        )

        Favourite.objects.create(user=self.user1, recipe=recipe1)
        Favourite.objects.create(user=self.user2, recipe=recipe1)
        Favourite.objects.create(user=self.user3, recipe=recipe1)

        Favourite.objects.create(user=self.user1, recipe=recipe2)
        Favourite.objects.create(user=self.user2, recipe=recipe2)

        response = self.client.get(self.browse_url + '?popular=1')
        self.assertEqual(response.status_code, 200)

        recipes = list(response.context['recipes'])
        self.assertEqual(recipes[0], recipe1)
        self.assertEqual(recipes[1], recipe2)
        self.assertEqual(recipes[2], recipe3)

    def test_recipes_with_zero_favourites_are_listed_last(self):
        Favourite.objects.create(user=self.user1, recipe=self.recipe1)

        response = self.client.get(self.browse_url + '?popular=1')
        self.assertEqual(response.status_code, 200)

        recipes = list(response.context['recipes'])
        self.assertEqual(recipes[0], self.recipe1)
        self.assertIn(self.recipe2, recipes[1:])
        self.assertIn(self.recipe3, recipes[1:])

    def test_default_ordering_ignores_popularity_when_popular_not_set(self):
        Favourite.objects.create(user=self.user1, recipe=self.recipe1)
        Favourite.objects.create(user=self.user2, recipe=self.recipe1)

        response = self.client.get(self.browse_url)
        self.assertEqual(response.status_code, 200)

        recipes = list(response.context['recipes'])
        self.assertIn(self.recipe1, recipes)
        self.assertIn(self.recipe2, recipes)