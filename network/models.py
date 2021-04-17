import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class TimestampedBaseModel(models.Model):
    """
    Base class for other models with UUID & timestamp
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        null=False
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        null=False
    )

    class Meta:
        abstract = True


class User(AbstractUser):
    """
    Django AbstractUser with UUID & functions added
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    def __str__(self):
        return self.username

    def get_posts(self):
        return Post.objects.filter(user_id=self.id)

    def get_followers(self):
        return Follow.objects.filter(user_id=self.id)

    def get_other_users_followed(self):
        return Follow.objects.filter(follower_id=self.id)

    def get_number_of_followers(self):
        return Follow.objects.filter(user_id=self.id).count()

    def get_number_of_other_users_followed(self):
        return Follow.objects.filter(follower_id=self.id).count()

    def get_posts_by_users_followed(self):
        users_followed = Follow.objects.filter(follower_id=self.id).values('user_id')
        return Post.objects.filter(user_id__in=users_followed)

    def get_liked_posts(self):
        post_ids = Like.objects.filter(related_user_id=self.id).values("post")
        return Post.objects.filter(id__in=post_ids)


class Post(TimestampedBaseModel):
    """
    Stores each user's posts
    """

    user = models.ForeignKey(
        'User',
        related_name='posts',
        verbose_name='User',
        on_delete=models.CASCADE
    )

    content = models.TextField(
        max_length=500
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Posts"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user} posted: {self.content}"

    def get_number_of_likes(self):
        return Like.objects.filter(post_id=self.id).count()

    """ returns a string showing latest interaction and whether it was a creation or edit  """

    def created_or_modified(self):
        created = self.created_at.strftime('%d-%m-%Y %H:%M')
        updated = self.updated_at.strftime('%d-%m-%Y %H:%M')
        if created != updated:
            return f"modified: {updated}"
        else:
            return f" created: {created}"


class Like(TimestampedBaseModel):
    """
    Class for registering 'likes' on user posts
    """

    """ link to the post """
    post = models.ForeignKey(
        'Post',
        related_name='likes',
        verbose_name='Post',
        on_delete=models.CASCADE
    )

    """ link to the user liking the post """
    related_user = models.ForeignKey(
        'User',
        related_name='liked',
        verbose_name='User',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-related_user']
        verbose_name_plural = "Likes"
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['related_user']),
        ]

    def __str__(self):
        return f"{self.related_user} liked post {self.post}"


class Follow(TimestampedBaseModel):
    """
    Class for registering choices to 'follow' specific users
    """

    """ account being followed """
    user = models.ForeignKey(
        'User',
        related_name='followers',
        verbose_name='User',
        on_delete=models.CASCADE
    )

    """ user who is following """
    follower = models.ForeignKey(
        'User',
        related_name='following',
        verbose_name='Follower',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['follower']
        verbose_name_plural = "Follows"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['follower']),
        ]

    def __str__(self):
        return f"{self.follower} followed {self.user}"
