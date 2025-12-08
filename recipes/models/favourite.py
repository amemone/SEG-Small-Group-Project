from django.db import models
from .user import User


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    favourited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['-favourited_at']

    def __str__(self):
        return f"{self.user.username} favourited {self.recipe.title}"
