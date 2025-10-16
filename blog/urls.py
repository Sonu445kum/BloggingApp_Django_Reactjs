# urls.py
from django.urls import path
from . import views

# -----------------------------
# Blog App URLs
# -----------------------------

urlpatterns = [

    # -------------------------
    # AUTH / USER
    # -------------------------
    path('auth/register/', views.register_view, name='register'),
    path('auth/current-user/', views.current_user_view, name='current-user'),
    path('auth/verify-email/', views.verify_email, name='verify-email'),
    path('auth/request-password-reset/', views.request_password_reset, name='request-password-reset'),
    path('auth/reset-password/', views.reset_password, name='reset-password'),
    path('auth/change-password/', views.change_password, name='change-password'),

    # -------------------------
    # PROFILE
    # -------------------------
    path('profile/status/', views.profile_status, name='profile-status'),
    path('activity-logs/', views.activity_logs, name='activity-logs'),

    # -------------------------
    # TAGS / SEARCH
    # -------------------------
    path('tags/suggestions/', views.tag_suggestions, name='tag-suggestions'),

    # -----------------------------
    # API endpoint for top 5 blogs
    # -----------------------------
    path('api/top-blogs/', views.top_blogs_api, name='top-blogs-api'),

    # -------------------------
    # BLOG CRUD
    # -------------------------
    path('blogs/', views.blog_list_view, name='blog-list'),
    path('blogs/trending/', views.trending_blogs_view, name='trending-blogs'),
    path('blogs/<int:pk>/', views.blog_detail_view, name='blog-detail'),
    path('blogs/create/', views.blog_create_view, name='blog-create'),
    path('blogs/<int:pk>/update/', views.blog_update_view, name='blog-update'),
    path('blogs/drafts/', views.draft_blogs_view, name='draft-blogs'),

    # -------------------------
    # BLOG MEDIA
    # -------------------------
    path('blogs/media/upload/', views.blog_media_upload_view, name='blog-media-upload'),

    # -------------------------
    # CATEGORIES
    # -------------------------
    path('categories/', views.category_list_view, name='category-list'),
    path('categories/create/', views.category_create_view, name='category-create'),
    path('categories/<int:pk>/update-delete/', views.category_update_delete_view, name='category-update-delete'),

    # -------------------------
    # BLOG APPROVAL / FLAG (Admin / Editor)
    # -------------------------
    path('blogs/<int:blog_id>/approve/', views.approve_blog, name='approve-blog'),
    path('blogs/<int:blog_id>/flag/', views.flag_blog, name='flag-blog'),

    # -------------------------
    # REACTIONS
    # -------------------------
    path('blogs/<int:blog_id>/reactions/toggle/', views.toggle_reaction, name='toggle-reaction'),
    path('blogs/<int:blog_id>/reactions/', views.reaction_list_view, name='reaction-list'),

    # -------------------------
    # COMMENTS
    # -------------------------
    path('blogs/<int:blog_id>/comments/', views.comment_list_view, name='comment-list'),
    path('blogs/<int:blog_id>/comments/add/', views.add_comment, name='add-comment'),
    path('comments/<int:pk>/delete/', views.comment_delete_view, name='comment-delete'),

    # -------------------------
    # BOOKMARKS
    # -------------------------
    path('blogs/<int:blog_id>/bookmark/', views.toggle_bookmark, name='toggle-bookmark'),
    path('user/bookmarks/', views.user_bookmarks, name='user-bookmarks'),

    # -------------------------
    # NOTIFICATIONS
    # -------------------------
    path('user/notifications/', views.user_notifications, name='user-notifications'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read_view, name='notification-mark-read'),

    # -------------------------
    # GENERAL STATS
    # -------------------------
    path('stats/', views.stats_view, name='stats'),

    # -------------------------
    # ADMIN DASHBOARD
    # -------------------------
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/users/', views.all_users, name='all-users'),
    path('admin/users/<int:user_id>/update-role/', views.update_user_role, name='update-user-role'),
    path('admin/most-active-users/', views.most_active_users, name='most-active-users'),
    path('admin/trending-blogs/', views.trending_blogs_admin, name='trending-blogs-admin'),
]
