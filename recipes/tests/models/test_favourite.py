from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from recipes.models import User, Recipe, Favourite
from time import sleep


class FavouriteModelTestCase(TestCase):
    """Tests for the favourite model."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.first_recipe = Recipe.objects.create(
            title='Cereal',
            description='Cereal, milk',
            user=self.user
        )
        self.second_recipe = Recipe.objects.create(
            title='Rice and beans',
            description='Rice, beans',
            user=self.user
        )
        self.first_favourite = Favourite.objects.create(
            user=self.user,
            recipe=self.first_recipe
        )

    def test_valid_favourite(self):
        try:
            self.first_favourite.full_clean()
        except ValidationError:
            self.fail("Favourite should be valid")

    def test_user_must_exist(self):
        self.first_favourite.user = None
        with self.assertRaises(ValidationError):
            self.first_favourite.full_clean()

    def test_recipe_must_exist(self):
        self.first_favourite.recipe = None
        with self.assertRaises(ValidationError):
            self.first_favourite.full_clean()

    def test_user_cannot_favourite_same_recipe_twice(self):
        with self.assertRaises(IntegrityError):
            Favourite.objects.create(user=self.user, recipe=self.first_recipe)

    def test_string_representation(self):
        string = str(self.first_favourite)
        expected = f"{self.user.username} favourited {self.first_recipe.title}"
        self.assertEqual(string, expected)

    def test_favourites_ordered_by_newest_first(self):
        sleep(0.01)
        second_favourite = Favourite.objects.create(
            user=self.user,
            recipe=self.second_recipe
        )
        favourites = list(Favourite.objects.filter(user=self.user))
        self.assertEqual(favourites, [second_favourite, self.first_favourite])
