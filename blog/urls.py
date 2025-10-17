# urls.py
from django.urls import path
from . import views

# ==============================================================
# BLOG APP URL CONFIGURATION
# --------------------------------------------------------------
# Yeh file app ke saare API endpoints ko map karti hai views ke saath
# ==============================================================

urlpatterns = [

    # ----------------------------------------------------------
    #  AUTHENTICATION & USER MANAGEMENT
    # ----------------------------------------------------------
    path('auth/register/', views.register_view, name='register'),                      # User registration
    path('auth/current-user/', views.current_user_view, name='current-user'),          # Get current logged-in user info
    path('auth/verify-email/', views.verify_email, name='verify-email'),               # Verify user email after registration
    path('auth/request-password-reset/', views.request_password_reset, name='request-password-reset'),  # Request password reset link
    path('auth/reset-password/', views.reset_password, name='reset-password'),         # Reset password via token
    path('auth/change-password/', views.change_password, name='change-password'),      # Change password (logged-in users only)

    # ----------------------------------------------------------
    #  USER PROFILE & ACTIVITY
    # ----------------------------------------------------------
    path('profile/status/', views.profile_status, name='profile-status'),              # View user profile status
    path('activity-logs/', views.activity_logs, name='activity-logs'),                 # View user activity logs

    # ----------------------------------------------------------
    #  TAGS & SEARCH
    # ----------------------------------------------------------
    path('tags/suggestions/', views.tag_suggestions, name='tag-suggestions'),          # Get tag suggestions for auto-complete

    # ----------------------------------------------------------
    #  TOP BLOGS API
    # ----------------------------------------------------------
    path('api/top-blogs/', views.top_blogs_api, name='top-blogs-api'),                 # Fetch top 5 blogs based on reactions

    # ----------------------------------------------------------
    #  BLOG CRUD (Create, Read, Update, Delete)
    # ----------------------------------------------------------
    path('blogs/', views.blog_list_view, name='blog-list'),                            # List all blogs
    path('blogs/trending/', views.trending_blogs_view, name='trending-blogs'),         # List trending blogs
    path('blogs/<int:pk>/', views.blog_detail_view, name='blog-detail'),               # View single blog details
    path('blogs/create/', views.blog_create_view, name='blog-create'),                 # Create a new blog
    path('blogs/<int:pk>/update/', views.blog_update_view, name='blog-update'),        # Update an existing blog
    path('blogs/drafts/', views.draft_blogs_view, name='draft-blogs'),                 # List user’s draft blogs

    # ----------------------------------------------------------
    #  BLOG MEDIA UPLOADS
    # ----------------------------------------------------------
    path('blogs/media/upload/', views.blog_media_upload_view, name='blog-media-upload'),  # Upload images/media for blogs

    # ----------------------------------------------------------
    #  CATEGORIES MANAGEMENT
    # ----------------------------------------------------------
    path('categories/', views.category_list_view, name='category-list'),               # List all categories
    path('categories/create/', views.category_create_view, name='category-create'),    # Create a new category
    path('categories/<int:pk>/update-delete/', views.category_update_delete_view, name='category-update-delete'),  # Update/Delete category

    # ----------------------------------------------------------
    #  BLOG APPROVAL &  FLAGGING (For Admin/Editor)
    # ----------------------------------------------------------
    path('blogs/<int:blog_id>/approve/', views.approve_blog, name='approve-blog'),     # Approve blog post
    path('blogs/<int:blog_id>/flag/', views.flag_blog, name='flag-blog'),              # Flag a blog post as inappropriate

    # ----------------------------------------------------------
    #  REACTIONS (Like / Unlike)
    # ----------------------------------------------------------
    path('blogs/<int:blog_id>/reactions/toggle/', views.toggle_reaction, name='toggle-reaction'),  # Toggle like/dislike
    path('blogs/<int:blog_id>/reactions/', views.reaction_list_view, name='reaction-list'),        # List all reactions for a blog

    # ----------------------------------------------------------
    #  COMMENTS SECTION
    # ----------------------------------------------------------
    path('blogs/<int:blog_id>/comments/', views.comment_list_view, name='comment-list'),           # List comments for a blog
    path('blogs/<int:blog_id>/comments/add/', views.add_comment, name='add-comment'),              # Add new comment
    path('comments/<int:pk>/delete/', views.comment_delete_view, name='comment-delete'),           # Delete a comment

    # ----------------------------------------------------------
    #  BOOKMARKS
    # ----------------------------------------------------------
    path('blogs/<int:blog_id>/bookmark/', views.toggle_bookmark, name='toggle-bookmark'),          # Add/Remove bookmark
    path('user/bookmarks/', views.user_bookmarks, name='user-bookmarks'),                          # Get all user bookmarks

    # ----------------------------------------------------------
    #  NOTIFICATIONS
    # ----------------------------------------------------------
    path('user/notifications/', views.user_notifications, name='user-notifications'),              # List user notifications
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read_view, name='notification-mark-read'),  # Mark notification as read

    # ----------------------------------------------------------
    #  GENERAL STATS
    # ----------------------------------------------------------
    path('stats/', views.stats_view, name='stats'),                                                # Get site-wide statistics

    # ----------------------------------------------------------
    #  ADMIN DASHBOARD
    # ----------------------------------------------------------
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),                       # Admin dashboard overview
    path('admin/users/', views.all_users, name='all-users'),                                       # List all users
    path('admin/users/<int:user_id>/update-role/', views.update_user_role, name='update-user-role'), # Update user role (Admin action)
    path('admin/most-active-users/', views.most_active_users, name='most-active-users'),            # View most active users
    path('admin/trending-blogs/', views.trending_blogs_admin, name='trending-blogs-admin'),         # Trending blogs (Admin view)
]
