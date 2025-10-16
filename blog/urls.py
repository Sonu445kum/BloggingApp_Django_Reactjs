from django.urls import path
from . import views

urlpatterns = [
    # -------------------------
    # AUTH
    # -------------------------
    path('auth/register/', views.register_view, name='register'),
    path('auth/me/', views.current_user_view, name='current_user'),
    path('auth/email-verify/', views.verify_email, name='verify-email'),
    path('auth/request-password-reset/', views.request_password_reset, name='request_password_reset'),
    path('auth/reset-password/', views.reset_password, name='reset_password'),
    path('auth/change-password/', views.change_password, name='change_password'),

    # -------------------------
    # PROFILE & USER ACTIVITY
    # -------------------------
    path('profile-status/', views.profile_status, name='profile-status'),
    path('activity-logs/', views.activity_logs, name='activity-logs'),

    # -------------------------
    # BLOGS
    # -------------------------
    path('blogs/', views.blog_list_view, name='blog_list'),
    path('blogs/trending/', views.trending_blogs_view, name='trending_blogs'),
    path('blogs/drafts/', views.draft_blogs_view, name='draft_blogs'),
    path('blogs/create/', views.blog_create_view, name='blog_create'),
    path('blogs/<int:pk>/', views.blog_detail_view, name='blog_detail'),
    path('blogs/<int:pk>/edit/', views.blog_update_view, name='blog_update'),
    path('blogs/media/upload/', views.blog_media_upload_view, name='blog_media_upload'),

    # -------------------------
    # CATEGORIES
    # -------------------------
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update_delete_view, name='category_update_delete'),

    # -------------------------
    # COMMENTS
    # -------------------------
    path('blogs/<int:blog_id>/comments/', views.comment_list_view, name='comment_list'),
    path('blogs/<int:blog_id>/comments/create/', views.comment_create_view, name='comment_create'),
    path('comments/<int:pk>/delete/', views.comment_delete_view, name='comment_delete'),

    # -------------------------
    # REACTIONS
    # -------------------------
    path('blogs/<int:blog_id>/reaction/', views.reaction_toggle_view, name='reaction_toggle'),
    path('blogs/<int:blog_id>/reactions/', views.reaction_list_view, name='reaction_list'),

    # -------------------------
    # NOTIFICATIONS
    # -------------------------
    path('notifications/', views.notification_list_view, name='notification_list'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read_view, name='notification_mark_read'),

    # -------------------------
    # ADMIN STATS
    # -------------------------
    path('stats/', views.stats_view, name='stats'),
]
