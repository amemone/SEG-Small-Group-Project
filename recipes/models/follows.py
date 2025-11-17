from django.contrib.auth.models import User
from django.db import models

class Follows():
    follower = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'followed_relationships'
    )

    followed = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'following_relationships'
    )

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower} follows {self.followed}"
    