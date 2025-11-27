from django.test import TestCase
from recipes.models import User
from django.urls import reverse
from recipes.models.recipes import Recipe

class RecipeBrowseTest(TestCase):
    """
    Test suite for recipe browse view"""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
    ]
    
    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        
        self.url = reverse('recipe_browse')

        self.first_recipe = Recipe.objects.create(
            title = 'Vanilla Cake',
            description = 'eggs, milk, flour, sugar, vanilla, icing',
            user = self.user
        )

        self.second_recipe = Recipe.objects.create(
            title = 'Chocolate Cake',
            description = 'eggs, milk, flour, sugar, chocolate icing',
            user = self.user
        )

        self.third_recipe = Recipe.objects.create(
            title = 'Caramel Brownies',
            description = 'eggs, milk, flour, sugar, cocoa powder, caramel',
            user = self.user
        )

    def test_browse_url(self):
        self.assertEqual(self.url, '/recipes/browse/')

    def test_search_title_returns_correct_recipe(self):
        response = self.client.get(self.url, {'q': 'Vanilla'})
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [self.first_recipe])

    def test_search_description_returns_correct_recipe(self):
        response = self.client.get(self.url, {'q': 'cocoa'})
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [self.third_recipe])

    def test_search_with_space_returns_no_recipes(self):
        response = self.client.get(self.url, {'q': ' '})
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [])

    def test_search_not_case_sensitive(self):
        response = self.client.get(self.url, {'q': 'cHocolAte'})
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [self.second_recipe])

    def test_search_works_with_spaces(self):
        response = self.client.get(self.url, {'q': ' Brownies   '})
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [self.third_recipe])

    def test_search_nonexistant_recipe(self):
        response = self.client.get(self.url, {'q': 'spaghetti'})
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [])

    def test_search_returns_multiple_recipes(self):
        response = self.client.get(self.url, {'q': 'Cake'})
        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [self.second_recipe, self.first_recipe])

    