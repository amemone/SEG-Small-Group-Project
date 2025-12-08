"""Unit tests for creating recipes with the RecipeForm."""

from django import forms
from django.test import TestCase
from recipes.forms.recipe_form import RecipeForm
from recipes.models import User
from recipes.models.recipes import Recipe


class CreateRecipeFormTestCase(TestCase):
    """Unit tests of the create recipe form."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='@johndoe',
            password='password123',
            email='johndoe@example.com'
        )

        self.form_input = {
            'title': 'Scrambled eggs',
            'description': 'Scrambled eggs recipe description',
            'visibility': 'public'
        }

    def test_form_contains_required_fields(self):
        form = RecipeForm()
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)

        self.assertIsInstance(form.fields['title'].widget, forms.TextInput)
        self.assertIsInstance(
            form.fields['description'].widget, forms.Textarea)

    def test_form_accepts_valid_input(self):
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_title(self):
        self.form_input['title'] = ''
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_description(self):
        self.form_input['description'] = ''
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        before = Recipe.objects.count()

        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        recipe = form.save(commit=False)
        recipe.user = self.user
        recipe.save()

        after = Recipe.objects.count()
        self.assertEqual(after, before + 1)

        self.assertEqual(recipe.title, 'Scrambled eggs')
        self.assertEqual(recipe.description,
                         'Scrambled eggs recipe description')
        self.assertEqual(recipe.user, self.user)

    def test_recipe_id_auto_increments(self):
        form = RecipeForm(data=self.form_input)
        recipe = form.save(commit=False)
        recipe.user = self.user
        recipe.save()

        self.assertIsNotNone(recipe.id)
        self.assertIsInstance(recipe.id, int)

    def test_created_recipe_appears_in_user_recipes(self):
        form = RecipeForm(data=self.form_input)
        recipe = form.save(commit=False)
        recipe.user = self.user
        recipe.save()

        self.assertIn(recipe, self.user.recipes.all())
