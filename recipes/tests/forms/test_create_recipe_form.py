from django.test import TestCase
from recipes.forms.recipe_form import RecipeForm
from recipes.models import Tag, Recipe, User


class RecipeFormTestCase(TestCase):
    """
    Unit tests for the RecipeForm.

    Tests form validation, cleaning methods, and field requirements
    for recipe creation and updates.
    """

    fixtures = ['recipes/tests/fixtures/default_user.json',
                'recipes/tests/fixtures/other_users.json']

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.user = User.objects.get(username='@johndoe')

        self.tag1, _ = Tag.objects.get_or_create(name='Vegetarian')
        self.tag2, _ = Tag.objects.get_or_create(name='Quick')

        # This assumes your Recipe model has DIFFICULTY_CHOICES
        difficulty_choices = Recipe._meta.get_field('difficulty').choices
        valid_difficulty = difficulty_choices[0][0] if difficulty_choices else ''

        self.form_input = {
            'title': 'Delicious Pasta',
            'description': 'A wonderful pasta dish with fresh ingredients and amazing flavors.',
            'visibility': 'public',
            'difficulty': valid_difficulty,
            'time_required': '30',
            'ingredients': 'Pasta 200 grams\nTomato Sauce 1 cup\nBasil 5 leaves',
            'tags': [self.tag1.id, self.tag2.id]
        }

    def test_form_has_necessary_fields(self):
        form = RecipeForm()
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('visibility', form.fields)
        self.assertIn('tags', form.fields)
        self.assertIn('ingredients', form.fields)
        self.assertIn('difficulty', form.fields)
        self.assertIn('time_required', form.fields)

    def test_valid_recipe_form(self):
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_title_cannot_be_empty(self):
        self.form_input['title'] = ''
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_title_cannot_be_blank(self):
        self.form_input['title'] = '   '
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_title_must_be_at_least_3_characters(self):
        self.form_input['title'] = 'AB'
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_title_can_be_exactly_3_characters(self):
        self.form_input['title'] = 'ABC'
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_title_strips_whitespace(self):
        self.form_input['title'] = '  Pasta Recipe  '
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Pasta Recipe')

    def test_description_cannot_be_empty(self):
        self.form_input['description'] = ''
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_description_cannot_be_blank(self):
        self.form_input['description'] = '   '
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_description_must_be_at_least_10_characters(self):
        self.form_input['description'] = 'Too short'
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_description_can_be_exactly_10_characters(self):
        self.form_input['description'] = '1234567890'
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_description_strips_whitespace(self):
        self.form_input['description'] = '  A delicious meal that everyone loves  '
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['description'], 'A delicious meal that everyone loves')

    def test_ingredients_field_is_optional(self):
        self.form_input['ingredients'] = ''
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_ingredients_accepts_multiline_text(self):
        self.form_input['ingredients'] = 'Flour 2 cups\nSugar 1 cup\nEggs 3 pieces'
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_tags_field_is_optional(self):
        self.form_input['tags'] = []
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_tags_accepts_multiple_values(self):
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data['tags']), 2)

    def test_time_required_is_optional(self):
        self.form_input['time_required'] = ''
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_time_required_accepts_valid_choice(self):
        valid_times = ['5', '10', '15', '20', '30', '45', '60', '90']
        for time_value in valid_times:
            self.form_input['time_required'] = time_value
            form = RecipeForm(data=self.form_input)
            self.assertTrue(
                form.is_valid(), f"Form should be valid with time_required={time_value}")

    def test_difficulty_field_exists(self):
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertIn('difficulty', form.cleaned_data)

    def test_visibility_field_exists(self):
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertIn('visibility', form.cleaned_data)

    def test_form_must_save_correctly(self):
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        recipe = form.save(commit=False)
        recipe.user = self.user
        recipe.save()
        form.save_m2m()

        self.assertEqual(recipe.title, 'Delicious Pasta')
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.tags.count(), 2)
