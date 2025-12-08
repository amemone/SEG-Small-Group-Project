from django.db import models
from django.conf import settings


class Follow(models.Model):
    """Model used to show a following relation between two users"""
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    followee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )
    date_followed = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model options."""
        unique_together = ("follower", "followee")

    def __str__(self):
        """Convert following relation to string."""
        return f"{self.follower.username} follows {self.followee.username}."
