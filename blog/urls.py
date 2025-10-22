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
    path('auth/register/', views.register_view, name='register'),  # User registration
    # User login with JWT
    path('auth/login/', views.login_view, name='login'),
    path('auth/current-user/', views.current_user_view,  name='current-user'),          # Get current logged-in user info
    # Verify user email after registration
    path('auth/verify-email/', views.verify_email, name='verify-email'),
    path('auth/request-password-reset/', views.request_password_reset, name='request-password-reset'),  # Request password reset link
    path('auth/reset-password/', views.reset_password, name='reset-password'),         # Reset password via token
    # Change password (logged-in users only)
    path('auth/change-password/', views.change_password, name='change-password'),

    # ----------------------------------------------------------
    #  USER PROFILE & ACTIVITY
    # ----------------------------------------------------------
    # View user profile status
    path('profile/status/', views.profile_status, name='profile-status'),
    # View user activity logs
    path('activity-logs/', views.activity_logs, name='activity-logs'),

    # ----------------------------------------------------------
    #  TAGS & SEARCH
    # ----------------------------------------------------------
    # Get tag suggestions for auto-complete
    path('tags/suggestions/', views.tag_suggestions, name='tag-suggestions'),

    # ----------------------------------------------------------
    #  TOP BLOGS API
    # ----------------------------------------------------------
    # Fetch top 5 blogs based on reactions
    path('api/top-blogs/', views.top_blogs_api, name='top-blogs-api'),

    # ----------------------------------------------------------
    #  BLOG CRUD (Create, Read, Update, Delete)
    # ----------------------------------------------------------
    # List all blogs
    path('blogs/', views.blog_list_view, name='blog-list'),
    path('blogs/trending/', views.trending_blogs_view, name='trending-blogs'),         # List trending blogs
    path('blogs/<int:pk>/', views.blog_detail_view, name='blog-detail'),               # View single blog details
    path('blogs/create/', views.blog_create_view, name='blog-create'),                 # Create a new blog
    path('blogs/<int:pk>/update/', views.blog_update_view, name='blog-update'),
    path('blogs/<int:pk>/delete/', views.blog_delete_view, name='blog-delete'),  # Update an existing blog
    
    # List user’s draft blogs
    path('blogs/drafts/', views.draft_blogs_view, name='draft-blogs'),

    # ----------------------------------------------------------
    #  BLOG MEDIA UPLOADS
    # ----------------------------------------------------------
    path('blogs/media/upload/', views.blog_media_upload_view, name='blog-media-upload'),  # Upload images/media for blogs

    # -----------------------------
    # List All Categories
    # -----------------------------
    path('categories/', views.category_list_view, name='category-list'),

    # -----------------------------
    # Create New Category
    # -----------------------------
    path('categories/create/', views.category_create_view, name='category-create'),

    # -----------------------------
    # Update / Delete Category
    # -----------------------------
    path('categories/<int:pk>/update-delete/', views.category_update_delete_view, name='category-update-delete'),



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
    # Get all user bookmarks
    path('user/bookmarks/', views.user_bookmarks, name='user-bookmarks'),

    # ----------------------------------------------------------
    #  NOTIFICATIONS API ROUTES
    # ----------------------------------------------------------

    #  Get all notifications for the logged-in user
    path('user/notifications/', views.user_notifications_view, name='user-notifications'),

    #  Mark a single notification as read (using notification ID)
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read_view, name='notification-mark-read'),

    #  Mark all notifications as read for the current user
    path('notifications/mark-all-read/', views.mark_all_notifications_read_view, name='notification-mark-all-read'),

    #  Delete a specific notification (by ID)
    path('notifications/<int:pk>/delete/', views.delete_notification_view, name='notification-delete'),

    # ----------------------------------------------------------
    #  GENERAL STATS
    # ----------------------------------------------------------
    # Get site-wide statistics
    path('stats/', views.stats_view, name='stats'),

    # ----------------------------------------------------------
    #  ADMIN DASHBOARD
    # ----------------------------------------------------------
    # Admin dashboard overview
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    # List all users
    path('admin/users/', views.all_users, name='all-users'),
    path('admin/users/<int:user_id>/update-role/', views.update_user_role, name='update-user-role'),  # Update user role (Admin action)
    path('admin/most-active-users/', views.most_active_users, name='most-active-users'),            # View most active users
    path('admin/trending-blogs/', views.trending_blogs_admin, name='trending-blogs-admin'),         # Trending blogs (Admin view)

    # ----------------------------------------------------------
    # BLOG APPROVAL & FLAGGING (For Admin/Editor)
    # ----------------------------------------------------------
    path('blogs/<int:blog_id>/approve/', views.approve_blog, name='approve-blog'),   # Approve blog post
    path('blogs/<int:blog_id>/flag/', views.flag_blog, name='flag-blog'),             # Flag blog post
]
