from django.contrib import admin
from .models import (
    CustomUser,
    Profile,
    Category,
    Blog,
    BlogMedia,
    Comment,
    Reaction,
    Notification
)

# ----------------------------
# Simple registrations
# ----------------------------
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(Notification)
admin.site.register(BlogMedia)

# ----------------------------
# BLOG ADMIN ENHANCEMENT
# ----------------------------
# Unregister default if already registered
# admin.site.unregister(Blog)

# Register Blog with enhanced display
admin.site.register(Blog, type('BlogAdmin', (admin.ModelAdmin,), {
    'list_display': (
        'title', 'author', 'status', 'category', 'views', 'likes', 'comments_count', 
        'is_featured', 'publish_at', 'published_at', 'created_at', 'updated_at'
    ),
    'list_filter': ('status', 'category', 'author', 'is_featured', 'created_at'),
    'search_fields': ('title', 'content', 'author__username', 'tags__name'),
    'ordering': ('-published_at',),
    'readonly_fields': ('views', 'likes', 'comments_count', 'published_at'),
}))
