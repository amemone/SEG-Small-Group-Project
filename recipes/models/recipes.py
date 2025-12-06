from django.db import models
from django.utils import timezone
from .user import User


class Tag(models.Model):
    """
    Model representing a tag for the recipes created by a user.

    Attributes:
        name (str): The name of the tag
    """
    name = models.CharField(max_length=25, unique=True)

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
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends'),
        ('me', 'Only Me'),
    ]

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100000)
    publication_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    id = models.AutoField(primary_key=True)
    tags = models.ManyToManyField(Tag, blank=True)
    favourites = models.ManyToManyField(
        User,
        related_name="favourite_recipes",
        through="Favourite",
        through_fields=("recipe", "user"),
        blank=True
    )
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='public'
    )

    class Meta:
        """Model options."""
        ordering = ['-publication_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        """Return string representation of the recipe."""
        return self.title
    

    def is_favourited(self, user):
        return self.favourites.filter(id=user.id).exists()

    def get_favourite_count(self):
        return self.favourites.count()