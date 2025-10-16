# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from django.conf import settings

# # CustomUser with profile picture and admin flag
# class CustomUser(AbstractUser):
#     is_admin = models.BooleanField(default=False)
#     profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

#     def __str__(self):
#         return self.username



# # Blog Categories
# class Category(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return self.name

# # Blog Model
# class Blog(models.Model):
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blogs')
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs')
#     image = models.ImageField(upload_to='blogs/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_published = models.BooleanField(default=True)
#     views = models.IntegerField(default=0)  # Optional blog views

#     def __str__(self):
#         return self.title

# # Comment Model
# class Comment(models.Model):
#     blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
#     author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'Comment by {self.author.username} on {self.blog.title}'

# # Likes Models
# class Like(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='likes')
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'blog')  # ek user ek blog ko sirf ek baar like kar sakta hai

#     def __str__(self):
#         return f"{self.user.username} likes {self.blog.title}"


# Modify our Model that is Blog
from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager


# ----------------------------
# USER & PROFILE
# ----------------------------
class CustomUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    ROLE_CHOICES = (
        ('author','Author'),
        ('editor','Editor'),
        ('admin','Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='author')

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    bookmarks = models.ManyToManyField('Blog', related_name='bookmarked_by', blank=True)

# ----------------------------
# CATEGORY & BLOG
# ----------------------------
class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    STATUS_CHOICES = (('draft','Draft'), ('published','Published'))
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = TaggableManager()
    featured_image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    attachments = models.FileField(upload_to='blog_files/', blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    publish_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

# ----------------------------
# REACTIONS
# ----------------------------
class Reaction(models.Model):
    REACTIONS = (('like','Like'),('love','Love'),('wow','Wow'))
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reactions')
    type = models.CharField(choices=REACTIONS, max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

# ----------------------------
# NOTIFICATIONS
# ----------------------------
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
