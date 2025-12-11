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
            difficulty='Beginner',
        )
        self.recipe2 = Recipe.objects.create(
            title='Recipe 2',
            description='desc',
            user=self.user1,
            difficulty='Intermediate'
        )
        self.recipe3 = Recipe.objects.create(
            title='Recipe 3',
            description='desc',
            user=self.user1,
            difficulty='Advanced'
        )
        self.browse_url = reverse('recipe_browse')

    def test_most_favourited_recipe_appears_first_when_sorted_by_popularity(self):
        Favourite.objects.create(user=self.user1, recipe=self.recipe1)
        Favourite.objects.create(user=self.user2, recipe=self.recipe1)
        Favourite.objects.create(user=self.user3, recipe=self.recipe1)

        Favourite.objects.create(user=self.user1, recipe=self.recipe2)
        Favourite.objects.create(user=self.user2, recipe=self.recipe2)

        response = self.client.get(self.browse_url + '?popular=1')
        self.assertEqual(response.status_code, 200)

        recipes = list(response.context['recipes'])
        self.assertEqual(recipes[0], self.recipe1)
        self.assertEqual(recipes[1], self.recipe2)
        self.assertEqual(recipes[2], self.recipe3)

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
    
    def test_sort_by_popilarity_for_beginner_recipes(self):
        beginner2 = Recipe.objects.create(
            title='Beginner 2',
            description='desc',
            user=self.user1,
            difficulty='Beginner',
        )

        Favourite.objects.create(user=self.user1, recipe=self.recipe1)
        Favourite.objects.create(user=self.user2, recipe=self.recipe1)
        Favourite.objects.create(user=self.user1, recipe=beginner2)

        response = self.client.get(self.browse_url + '?popular=1&difficulty=Beginner')
        self.assertEqual(response.status_code, 200)

        recipes = list(response.context['recipes'])
        self.assertEqual(recipes[0], self.recipe1)
        self.assertEqual(recipes[1], beginner2)
        self.assertNotIn(self.recipe2, recipes)
        self.assertNotIn(self.recipe3, recipes)

    def test_sort_by_popilarity_for_intermediate_recipes(self):
        intermediate2 = Recipe.objects.create(
            title='Intermediate 2',
            description='desc',
            user=self.user1,
            difficulty='Intermediate',
        )

        Favourite.objects.create(user=self.user1, recipe=self.recipe2)
        Favourite.objects.create(user=self.user2, recipe=self.recipe2)
        Favourite.objects.create(user=self.user1, recipe=intermediate2)

        response = self.client.get(self.browse_url + '?popular=1&difficulty=Intermediate')
        self.assertEqual(response.status_code, 200)

        recipes = list(response.context['recipes'])
        self.assertEqual(recipes[0], self.recipe2)
        self.assertEqual(recipes[1], intermediate2)
        self.assertNotIn(self.recipe1, recipes)
        self.assertNotIn(self.recipe3, recipes)

    def test_sort_by_popilarity_for_advanced_recipes(self):
        advanced2 = Recipe.objects.create(
            title='Advanced 2',
            description='desc',
            user=self.user1,
            difficulty='Advanced',
        )

        Favourite.objects.create(user=self.user1, recipe=self.recipe3)
        Favourite.objects.create(user=self.user2, recipe=self.recipe3)
        Favourite.objects.create(user=self.user1, recipe=advanced2)

        response = self.client.get(self.browse_url + '?popular=1&difficulty=Advanced')
        self.assertEqual(response.status_code, 200)

        recipes = list(response.context['recipes'])
        self.assertEqual(recipes[0], self.recipe3)
        self.assertEqual(recipes[1], advanced2)
        self.assertNotIn(self.recipe1, recipes)
        self.assertNotIn(self.recipe2, recipes)