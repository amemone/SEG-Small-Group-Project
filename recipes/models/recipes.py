from django.db import models
from django.utils import timezone
from .user import User


class Recipe(models.Model):
    """
    Model representing a recipe created by a user.

    Attributes:
        title (str): The title of the recipe.
        description (str): Detailed description of the recipe.
        user (User): The user who created this recipe.
        publication_date (datetime): Timestamp when the recipe was published.
    """

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100000)
    publication_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    id = models.AutoField(primary_key=True)

    class Meta:
        """Model options."""
        ordering = ['-publication_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        """Return string representation of the recipe."""
        return self.title
