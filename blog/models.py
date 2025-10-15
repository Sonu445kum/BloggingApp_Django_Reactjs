from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended User model with profile picture and admin flag"""
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Category(models.Model):
    """Blog Category model"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Blog(models.Model):
    """Main Blog model"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        'blog.CustomUser',  # 👈 Always use app.Model format (safe for migrations)
        on_delete=models.CASCADE,
        related_name='blogs'
    )
    category = models.ForeignKey(
        'blog.Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogs'
    )
    image = models.ImageField(upload_to='blogs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comment model for each blog"""
    blog = models.ForeignKey(
        'blog.Blog',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        'blog.CustomUser',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.blog.title}"
