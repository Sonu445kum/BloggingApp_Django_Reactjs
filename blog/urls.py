from django.urls import path
from . import views

urlpatterns = [
    # -------------------------
    # AUTHENTICATION
    # -------------------------
    path('auth/register/', views.register_view, name='register'),  
    # Register a new user

    path('auth/me/', views.current_user_view, name='current_user'),  
    # Get details of the currently logged-in user

    path('auth/email-verify/', views.verify_email, name='verify-email'),  
    # Verify user's email using a token

    path('auth/request-password-reset/', views.request_password_reset, name='request_password_reset'),  
    # Request a password reset link via email

    path('auth/reset-password/', views.reset_password, name='reset_password'),  
    # Reset password using token and user ID

    path('auth/change-password/', views.change_password, name='change_password'),  
    # Change password while logged in

    # -------------------------
    # PROFILE & USER ACTIVITY
    # -------------------------
    path('profile-status/', views.profile_status, name='profile_status'),  
    # Check profile completion percentage

    path('activity-logs/', views.activity_logs, name='activity_logs'),  
    # Get all activity logs for the logged-in user

    # -------------------------
    # BLOGS
    # -------------------------
    path('blogs/', views.blog_list_view, name='blog_list'),  
    # List all published blogs, with optional search/filter parameters

    path('blogs/create/', views.blog_create_view, name='blog_create'),  
    # Create a new blog post

    path('blogs/<int:pk>/', views.blog_update_view, name='blog_update'),  
    # Update an existing blog (only the author can edit)

    path('blogs/<int:pk>/detail/', views.blog_detail_view, name='blog_detail'),  
    # Retrieve detailed information of a single blog

    path('blogs/drafts/', views.draft_blogs_view, name='draft_blogs'),  
    # Get all draft blogs for the logged-in user

    path('blogs/trending/', views.trending_blogs_view, name='trending_blogs'),  
    # Get the list of trending blogs

    path('blogs/<int:blog_id>/react/', views.toggle_reaction, name='toggle_reaction'),  
    # Add, update, or remove reaction (like, love, laugh, angry, dislike) on a blog

    path('blogs/<int:blog_id>/comments/', views.comment_list_view, name='comment_list'),  
    # List all top-level comments for a specific blog

    path('blogs/<int:blog_id>/comment/', views.add_comment, name='add_comment'),  
    # Add a comment to a blog, optionally as a reply to another comment

    path('comments/<int:pk>/delete/', views.comment_delete_view, name='comment_delete'),  
    # Delete a comment (only the author of the comment can delete it)

    path('blogs/<int:blog_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),  
    # Add or remove a bookmark for a specific blog

    path('bookmarks/', views.user_bookmarks, name='user_bookmarks'),  
    # Get all bookmarked blogs of the logged-in user

    path('blogs/search/', views.blog_list_view, name='search_blogs'),  
    # Search blogs by title, content, category, tag, or author

    # -------------------------
    # TAGS
    # -------------------------
    path('tags/suggest/', views.tag_suggestions, name='tag_suggestions'),  
    # Autocomplete tag suggestions based on query parameter

    # -------------------------
    # CATEGORIES
    # -------------------------
    path('categories/', views.category_list_view, name='category_list'),  
    # List all categories

    path('categories/create/', views.category_create_view, name='category_create'),  
    # Create a new category

    path('categories/<int:pk>/edit/', views.category_update_delete_view, name='category_update_delete'),  
    # Update or delete a specific category

    # -------------------------
    # NOTIFICATIONS
    # -------------------------
     path('notifications/', views.user_notifications, name='user_notifications'),  
    # List all notifications for the logged-in user

    path('notifications/<int:pk>/mark-read/', views.notification_mark_read_view, name='notification_mark_read'),  
    # Mark a specific notification as read

    # -------------------------
    # ADMIN STATS
    # -------------------------
    path('stats/', views.stats_view, name='stats'),  
    # Retrieve admin statistics: total users, blogs, comments, reactions, notifications
]
