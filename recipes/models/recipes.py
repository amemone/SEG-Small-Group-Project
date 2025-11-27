from django.db import models
from django.utils import timezone
from .user import User

class Tag(models.Model):
    """
    Model representing a tag for the recipes created by a user.
    
    Attributes:
        name (str): The name of the tag
    """
    name = models.CharField(max_length=25, unique = True)

    def __str__(self):
       return self.name

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
    description = models.CharField(max_length=1000)
    # Changed to DateTimeField with default
    publication_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    
    tags = models.ManyToManyField(Tag, blank = True)

    class Meta:
        """Model options."""
        ordering = ['-publication_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        """Return string representation of the recipe."""
        return self.title
