from django.urls import path
from .views import RegisterView, UserDetailView, BlogListCreateView, BlogDetailView, CategoryListCreateView, CommentListCreateView

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', UserDetailView.as_view(), name='user_detail'),

    # Blog APIs
    path('blogs/', BlogListCreateView.as_view(), name='blog_list_create'),
    path('blogs/<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),

    # Category APIs
    path('categories/', CategoryListCreateView.as_view(), name='category_list_create'),

    # Comment APIs
    path('blogs/<int:blog_id>/comments/', CommentListCreateView.as_view(), name='comment_list_create'),
]
