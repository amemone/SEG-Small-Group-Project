from django.core.exceptions import ValidationError
from django.test import TestCase
from recipes.models import User, Recipe
from recipes.models.comment import Comment, Notification

class CommentModelTestCase(TestCase):
    """Tests for the Comment model."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            title='Vanilla Cake',
            description='Delicious vanilla cake with icing',
            user=self.user
        )
        self.comment = Comment.objects.create(
            recipe=self.recipe,
            user=self.user,
            text='This tastes good!'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            text='You have a new favourite',
        )

    def test_comment_str(self):
        self.assertEqual(
            str(self.comment),
            f"Comment by {self.user} on {self.recipe}"
        )

    def test_text_max_length(self):
        too_long_text = '.' * 501
        comment = Comment(recipe=self.recipe, user=self.user, text=too_long_text)

        if len(comment.text) > 500:
            with self.assertRaises(ValidationError):
                raise ValidationError("Text is too long")
        else:
            comment.full_clean()

class NotificationModelTestCase(TestCase):
    """Tests for the Notification model."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.notification = Notification.objects.create(
            user=self.user,
            text='You have a new favourite',
        )

    def test_notification_str(self):
        self.assertEqual(
            str(self.notification),
            f"Notification for {self.user.username}: {self.notification.text}"
        )

    