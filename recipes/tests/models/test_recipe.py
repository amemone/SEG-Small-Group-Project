"""Unit tests for the Recipe model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from recipes.models import Recipe, User, Tag


class RecipeModelTestCase(TestCase):
    """Unit tests for the Recipe model."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.second_user = User.objects.get(username='@janedoe')

        self.tag1, _ = Tag.objects.get_or_create(name='Vegetarian')
        self.tag2, _ = Tag.objects.get_or_create(name='Quick')

        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='This is a test recipe with enough characters.',
            ingredients='Flour 2 cups\nSugar 1 cup\nEggs 3 pieces',
            user=self.user,
            visibility='public',
            difficulty='Beginner',
            time_required='30'
        )

    def test_valid_recipe(self):
        self._assert_recipe_is_valid()

    def test_title_cannot_be_blank(self):
        self.recipe.title = ''
        self._assert_recipe_is_invalid()

    def test_title_can_be_100_characters_long(self):
        self.recipe.title = 'x' * 100
        self._assert_recipe_is_valid()

    def test_title_cannot_be_over_100_characters_long(self):
        self.recipe.title = 'x' * 101
        self._assert_recipe_is_invalid()

    def test_title_need_not_be_unique(self):
        second_recipe = Recipe.objects.create(
            title='Another Recipe',
            description='Another test recipe description.',
            user=self.second_user
        )
        second_recipe.title = self.recipe.title
        self._assert_recipe_is_valid(second_recipe)

    def test_description_cannot_be_blank(self):
        self.recipe.description = ''
        self._assert_recipe_is_invalid()

    def test_description_can_be_very_long(self):
        self.recipe.description = 'x' * 10000
        self._assert_recipe_is_valid()

    def test_ingredients_can_be_blank(self):
        self.recipe.ingredients = ''
        self._assert_recipe_is_valid()

    def test_ingredients_accepts_multiline_text(self):
        self.recipe.ingredients = 'Ingredient 1\nIngredient 2\nIngredient 3'
        self._assert_recipe_is_valid()

    def test_user_must_be_assigned(self):
        self.recipe.user = None
        self._assert_recipe_is_invalid()

    def test_publication_date_defaults_to_now(self):
        recipe = Recipe.objects.create(
            title='New Recipe',
            description='A new test recipe.',
            user=self.user
        )
        self.assertIsNotNone(recipe.publication_date)
        time_difference = timezone.now() - recipe.publication_date
        self.assertTrue(time_difference.total_seconds() < 5)

    def test_visibility_defaults_to_public(self):
        recipe = Recipe.objects.create(
            title='New Recipe',
            description='A new test recipe.',
            user=self.user
        )
        self.assertEqual(recipe.visibility, 'public')

    def test_visibility_can_be_public(self):
        self.recipe.visibility = 'public'
        self._assert_recipe_is_valid()

    def test_visibility_can_be_friends(self):
        self.recipe.visibility = 'friends'
        self._assert_recipe_is_valid()

    def test_visibility_can_be_me(self):
        self.recipe.visibility = 'me'
        self._assert_recipe_is_valid()

    def test_visibility_cannot_be_invalid_choice(self):
        self.recipe.visibility = 'invalid'
        self._assert_recipe_is_invalid()

    def test_difficulty_defaults_to_beginner(self):
        recipe = Recipe.objects.create(
            title='New Recipe',
            description='A new test recipe.',
            user=self.user
        )
        self.assertEqual(recipe.difficulty, 'Beginner')

    def test_difficulty_can_be_beginner(self):
        self.recipe.difficulty = 'Beginner'
        self._assert_recipe_is_valid()

    def test_difficulty_can_be_intermediate(self):
        self.recipe.difficulty = 'Intermediate'
        self._assert_recipe_is_valid()

    def test_difficulty_can_be_advanced(self):
        self.recipe.difficulty = 'Advanced'
        self._assert_recipe_is_valid()

    def test_difficulty_cannot_be_invalid_choice(self):
        self.recipe.difficulty = 'Expert'
        self._assert_recipe_is_invalid()

    def test_time_required_can_be_blank(self):
        self.recipe.time_required = ''
        self._assert_recipe_is_valid()

    def test_time_required_can_store_value(self):
        self.recipe.time_required = '45'
        self._assert_recipe_is_valid()
        self.assertEqual(self.recipe.time_required, '45')

    def test_tags_can_be_empty(self):
        self.assertEqual(self.recipe.tags.count(), 0)

    def test_multiple_tags_can_be_added(self):
        self.recipe.tags.add(self.tag1, self.tag2)
        self.assertEqual(self.recipe.tags.count(), 2)

    def test_is_favourited_returns_false_when_not_favourited(self):
        self.assertFalse(self.recipe.is_favourited(self.second_user))

    def test_is_favourited_returns_true_when_favourited(self):
        self.recipe.favourites.add(self.second_user)
        self.assertTrue(self.recipe.is_favourited(self.second_user))

    def test_get_favourite_count_returns_zero_with_no_favourites(self):
        self.assertEqual(self.recipe.get_favourite_count(), 0)

    def test_get_favourite_count_returns_correct_count(self):
        self.recipe.favourites.add(self.second_user)
        self.assertEqual(self.recipe.get_favourite_count(), 1)

    def test_get_favourite_count_with_multiple_users(self):
        self.recipe.favourites.add(self.second_user)
        third_user = User.objects.create(
            username='@charlie',
            first_name='Charlie',
            last_name='Brown',
            email='charlie@example.com'
        )
        self.recipe.favourites.add(third_user)
        self.assertEqual(self.recipe.get_favourite_count(), 2)

    def test_user_can_have_multiple_recipes(self):
        second_recipe = Recipe.objects.create(
            title='Second Recipe',
            description='Another recipe by the same user.',
            user=self.user
        )
        self.assertEqual(self.user.recipes.count(), 2)

    def test_deleting_user_deletes_recipes(self):
        recipe_id = self.recipe.id
        self.user.delete()
        with self.assertRaises(Recipe.DoesNotExist):
            Recipe.objects.get(id=recipe_id)

    def _assert_recipe_is_valid(self, recipe=None):
        if recipe is None:
            recipe = self.recipe
        try:
            recipe.full_clean()
        except ValidationError:
            self.fail('Test recipe should be valid')

    def _assert_recipe_is_invalid(self, recipe=None):
        if recipe is None:
            recipe = self.recipe
        with self.assertRaises(ValidationError):
            recipe.full_clean()
