from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from markdownx.models import MarkdownxField

# ----------------------------
# USER & PROFILE
# ----------------------------
class CustomUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    ROLE_CHOICES = (
        ('author', 'Author'),
        ('editor', 'Editor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='author')

    def __str__(self):
        return self.username


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    bookmarks = models.ManyToManyField('Blog', related_name='bookmarked_by', blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

# ----------------------------
# CATEGORY & BLOG
# ----------------------------
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)


    def __str__(self):
        return self.name


class Blog(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=255)
    content = CKEditor5Field('Content', config_name='default')
    markdown_content = MarkdownxField(blank=True, null=True)  # Markdown support
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs')
    tags = TaggableManager()
    featured_image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    attachments = models.FileField(upload_to='blog_files/', blank=True, null=True)

    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    publish_at = models.DateTimeField(null=True, blank=True)  # Scheduled publishing
    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def publish(self):
        """Publish immediately"""
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()

    def is_scheduled(self):
        """Check if blog is scheduled for future"""
        return self.publish_at and self.publish_at > timezone.now()

    def save(self, *args, **kwargs):
        """Auto-publish if publish_at is in the past"""
        if self.publish_at and self.publish_at <= timezone.now():
            self.status = 'published'
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


# ----------------------------
# BLOG MEDIA
# ----------------------------
class BlogMedia(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='blog_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# ----------------------------
# COMMENTS
# ----------------------------
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"


# ----------------------------
# REACTIONS
# ----------------------------
class Reaction(models.Model):
    REACTIONS = (
        ('like', 'Like'),
        ('love', 'Love'),
        ('wow', 'Wow')
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reactions')
    type = models.CharField(max_length=10, choices=REACTIONS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reacted {self.type} on {self.blog.title}"


# ----------------------------
# NOTIFICATIONS
# ----------------------------
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
