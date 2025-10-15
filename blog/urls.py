from django.urls import path
from . import views

urlpatterns = [
    # -------------------------
    # Auth
    # -------------------------
    path('auth/register/', views.register_view, name='register'),
    path('auth/me/', views.current_user_view, name='current_user'),

    # -------------------------
    # Blogs
    # -------------------------
    path('blogs/', views.blog_list_view, name='blog_list'),
    path('blogs/<int:pk>/', views.blog_detail_view, name='blog_detail'),
    path('blogs/create/', views.blog_create_view, name='blog_create'),
    path('blogs/<int:pk>/edit/', views.blog_update_delete_view, name='blog_update_delete'),

    # -------------------------
    # Categories
    # -------------------------
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update_delete_view, name='category_update_delete'),

    # -------------------------
    # Comments
    # -------------------------
    path('blogs/<int:blog_id>/comments/', views.comment_list_view, name='comment_list'),
    path('blogs/<int:blog_id>/comments/create/', views.comment_create_view, name='comment_create'),
    path('comments/<int:pk>/delete/', views.comment_delete_view, name='comment_delete'),


    # Likes
    path('likes/', views.like_list_create, name='like-list-create'),
    path('likes/<int:pk>/', views.like_detail, name='like-detail'),

    # -------------------------
    # Admin Stats
    # -------------------------
    path('stats/', views.stats_view, name='stats'),
]
