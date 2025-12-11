"""Unit tests of the comment form."""
from django import forms
from django.test import TestCase
from recipes.forms.comment_form import CommentForm
from recipes.models import User, Comment, Recipe


class CommentFormTestCase(TestCase):
    """Unit tests of the comment form."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test description',
            user=self.user
        )
        self.form_input = {'text': 'Test comment.'}

    def test_form_contains_required_fields(self):
        form = CommentForm()
        self.assertIn('text', form.fields)
        text_field = form.fields['text']
        self.assertTrue(isinstance(text_field.widget, forms.Textarea))
        self.assertEqual(text_field.widget.attrs['rows'], 3)
        self.assertEqual(text_field.widget.attrs['placeholder'], 'Write a comment...')

    def test_form_accepts_valid_input(self):
        form = CommentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_text(self):
        self.form_input['text'] = ''
        form = CommentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    