from django.db import models
from .user import User
from recipes.models.recipes import Recipe

class Comment(models.Model):
    """
    Model representing adding comments to recipes created by a user.
    
    Attributes: 
        recipe (Recipe): The recipe to comment on
        user (User): The user who is commenting
        text (str): The actual comment
        created_at (datetime): The time the comment was created
    """
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="comments")
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.recipe}"
    
class Notification(models.Model):
    """
    Model representing receiving notifications from likes and comments by a user
    
    Attributes: 
        user (User): The user who is gave the notification
        text (str): The actual notification
        link (URL): The link to the recipe
        is_read (bool): Whether the notification has been read
        created_at (datetime): The time the notification was created
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    text = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.text}"
