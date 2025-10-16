from django.urls import path
from . import views

urlpatterns = [
    
    # AUTH - Password Reset & Change
    # -------------------------
    path('auth/password-reset/request/', views.request_password_reset, name='request_password_reset'),
    path('auth/password-reset/confirm/', views.reset_password, name='reset_password'),
    path('auth/password-change/', views.change_password, name='change_password'),
    
    # -------------------------
    # AUTH
    # -------------------------
    # -------------------------

    path('auth/register/', views.register_view, name='register'),
    path('auth/me/', views.current_user_view, name='current_user'),
    path('auth/email-verify/', views.verify_email, name='email-verify'),

    # -------------------------
    # BLOGS
    # -------------------------
    path('blogs/', views.blog_list_view, name='blog_list'),
    path('blogs/<int:pk>/', views.blog_detail_view, name='blog_detail'),
    path('blogs/create/', views.blog_create_view, name='blog_create'),
    path('blogs/<int:pk>/edit/', views.blog_update_delete_view, name='blog_update_delete'),

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
