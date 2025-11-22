from django.contrib.auth.models import AbstractUser
from django.db import models
from .user import User

class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    followee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    date_followed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followee")

    def __str__(self):
        return f"{self.follower.username} follows {self.followee.username}."
