# -------------------------
# Django & Python imports
# -------------------------
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q, Count

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator

# -------------------------
# JWT & auth tokens
# -------------------------
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

# -------------------------
# Channels / WebSockets
# -------------------------
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# -------------------------
# Tags & Notifications
# -------------------------
from taggit.models import Tag
from webpush import send_user_notification

# -------------------------
# Custom permissions
# -------------------------
from .permissions import IsAdmin, IsEditor



# -------------------------
# Models & Serializers
# -------------------------
from .models import (
    CustomUser, Profile, Category, Blog, BlogMedia, Comment,
    Reaction, Notification, UserActivity, Bookmark
)
from .serializers import (
    CustomUserSerializer, ProfileSerializer, CategorySerializer, BlogSerializer,
    BlogMediaSerializer, CommentSerializer, ReactionSerializer,
    NotificationSerializer, RegisterSerializer, LoginSerializer
)
from .utils import profile_completion

from taggit.models import Tag
from rest_framework.permissions import IsAdminUser





@api_view(['POST'])
@permission_classes([IsAuthenticated])  # User ko login hona chahiye
def flag_blog(request, blog_id):
    """
    User ke liye blog ko inappropriate mark karne ka endpoint
    URL: /blogs/<int:blog_id>/flag/
    Method: POST
    """
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)

    # Agar already flagged hai
    if request.user in blog.flagged_by.all():
        return Response({'message': 'You have already flagged this blog'}, status=status.HTTP_200_OK)

    # Flagging logic (assuming Blog model me ManyToMany field 'flagged_by' hai)
    blog.flagged_by.add(request.user)
    blog.save()

    return Response({'message': 'Blog flagged successfully'}, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([IsAdminUser])  # Sirf admin approve kar sakta hai
def approve_blog(request, blog_id):
    """
    Admin ke liye blog approve karne ka endpoint
    URL: /blogs/<int:blog_id>/approve/
    Method: POST
    """
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)

    if blog.is_approved:  # Agar already approved hai
        return Response({'message': 'Blog is already approved'}, status=status.HTTP_200_OK)

    blog.is_approved = True
    blog.approved_by = request.user  # Agar model me approved_by field hai
    blog.approved_at = timezone.now()  # Agar model me approved_at field hai
    blog.save()

    return Response({'message': 'Blog approved successfully'}, status=status.HTTP_200_OK)





@api_view(['GET'])
@permission_classes([AllowAny])
def top_blogs_api(request):
    """
    API to fetch top 5 blogs based on number of reactions
    """
    top_blogs = Blog.objects.annotate(
        reactions_count=Count('reaction')
    ).order_by('-reactions_count')[:5]

    # Serialize data manually (or use a serializer if you have one)
    data = []
    for blog in top_blogs:
        data.append({
            'id': blog.id,
            'title': blog.title,
            'author': blog.author.username,
            'reactions_count': blog.reactions_count,
            'created_at': blog.created_at,
        })

    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def tag_suggestions(request):
    q = request.query_params.get('q', '').strip()
    if not q:
        return Response([])
    tags = Tag.objects.filter(name__istartswith=q).values_list('name', flat=True)[:10]
    return Response(list(tags))



# ----------------------------
# 🔹 PROFILE STATUS VIEW
# ----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_status(request):
    user = request.user
    completion = profile_completion(user)

    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": getattr(user, 'role', 'reader'),
        "email_verified": getattr(user, 'email_verified', False),
        "profile_completion": completion
    }
    return Response(data, status=status.HTTP_200_OK)




# ----------------------------
# 🔹 ACTIVITY LOGS VIEW
# ----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_logs(request):
    """
    Return a list of recent user activities for the logged-in user.
    """
    user = request.user
    logs = UserActivity.objects.filter(user=user).order_by('-timestamp')[:20]

    log_data = [
        {
            "activity_type": log.activity_type,
            "description": log.description,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for log in logs
    ]

    return Response({
        "user": user.username,
        "total_logs": len(log_data),
        "recent_activities": log_data
    }, status=status.HTTP_200_OK)




# -----------------------------
# USER DATA CLEAN HELPER
# -----------------------------
def clean_user_data(user):
    """Return user dict without first_name/last_name"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "email_verified": user.email_verified
    }



# -----------------------------
# JWT TOKENS HELPER
# -----------------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }




# -----------------------------
# REGISTER VIEW
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)

        # Generate email verification UID and token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_link = f"{settings.FRONTEND_URL}/verify-email/?uid={uid}&token={token}"

        # Send verification email
        send_mail(
            'Verify Your Email',
            f'Hi {user.username}, click the link to verify your email: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

        return Response({
            "message": "User registered successfully! Check your email for verification link.",
            "user": clean_user_data(user),
            "tokens": tokens
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# -----------------------------
# LOGIN VIEW
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({
            "message": "Login successful",
            "user": clean_user_data(user),
            "tokens": tokens
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# -----------------------------
# CURRENT USER VIEW
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    return Response(clean_user_data(request.user))






# -----------------------------
# VERIFY EMAIL VIEW
# -----------------------------
from django.utils.http import urlsafe_base64_decode
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
    uidb64 = request.GET.get('uid')
    token = request.GET.get('token')

    if not uidb64 or not token:
        return Response({'error': 'Missing uid or token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Decode the UID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        return Response({'error': 'Invalid UID'}, status=status.HTTP_400_BAD_REQUEST)

    # Check token validity
    if default_token_generator.check_token(user, token):
        if user.email_verified:
            return Response({'message': 'Email already verified'}, status=status.HTTP_200_OK)
        
        # Mark email as verified
        user.email_verified = True
        user.save()
        return Response({'message': 'Email successfully verified'}, status=status.HTTP_200_OK)
    
    return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# REQUEST PASSWORD RESET
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'No user found with this email'}, status=status.HTTP_404_NOT_FOUND)

    # Generate UID and token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/reset-password/?uid={uid}&token={token}"

    # Send reset email
    send_mail(
        'Password Reset Request',
        f'Hi {user.username}, click the link to reset your password: {reset_url}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    return Response({'message': 'Password reset link sent to email'}, status=status.HTTP_200_OK)




# -----------------------------
# RESET PASSWORD
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    if not uidb64 or not token or not new_password:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Decode UID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        return Response({'error': 'Invalid UID'}, status=status.HTTP_400_BAD_REQUEST)

    # Check token validity
    if not PasswordResetTokenGenerator().check_token(user, token):
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    # Set new password
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)


# -----------------------------
# CHANGE PASSWORD (Authenticated)
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response({'error': 'Both current and new passwords are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    if not user.check_password(current_password):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)





# -----------------------------
# BLOGS
# -----------------------------

# Blogs Create
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def blog_create_view(request):
    serializer = BlogSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Blogs Update View
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def blog_update_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if blog.author != request.user:
        return Response({'error': "You cannot edit someone else's blog"}, status=status.HTTP_403_FORBIDDEN)
    serializer = BlogSerializer(blog, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Blogs Delete 
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def blog_delete_view(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Only author can delete
    if blog.author != request.user:
        return Response({"error": "You are not allowed to delete this blog"}, status=status.HTTP_403_FORBIDDEN)
    
    blog.delete()
    return Response({"message": "Blog deleted successfully"}, status=status.HTTP_200_OK)

# Blogs List Views
@api_view(['GET'])
@permission_classes([AllowAny])
def blog_list_view(request):
    search = request.query_params.get('search', '')
    category = request.query_params.get('category', '')
    tag = request.query_params.get('tag', '')
    author = request.query_params.get('author', '')
    blogs = Blog.objects.filter(status='published')
    if search:
        blogs = blogs.filter(Q(title__icontains=search) | Q(content__icontains=search))
    if category:
        blogs = blogs.filter(category__name__iexact=category)
    if tag:
        blogs = blogs.filter(tags__name__iexact=tag)
    if author:
        blogs = blogs.filter(author__username__iexact=author)
    blogs = blogs.order_by('-published_at')
    serializer = BlogSerializer(blogs, many=True, context={'request': request})
    return Response(serializer.data)


# Drafts Blogs
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # only logged in users can access
def draft_blogs_view(request):
    # Sirf current user ke drafts
    drafts = Blog.objects.filter(author=request.user, status='draft')
    serializer = BlogSerializer(drafts, many=True)
    return Response(serializer.data)


# Blog Details 
@api_view(['GET'])
@permission_classes([AllowAny])
def blog_detail_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    serializer = BlogSerializer(blog, context={'request': request})
    return Response(serializer.data)


# Trending Blogs
@api_view(['GET'])
@permission_classes([AllowAny])
def trending_blogs_view(request):
    blogs = Blog.objects.filter(status='published').order_by('-views')[:10]
    serializer = BlogSerializer(blogs, many=True, context={'request': request})
    return Response(serializer.data)


# Blogs Media Upload
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def blog_media_upload_view(request):
    """
    Upload images for a blog.
    Expected fields:
    - blog_id (int)
    - file (image)
    """
    blog_id = request.data.get('blog_id')
    file = request.FILES.get('file')  # image file

    if not blog_id or not file:
        return Response({"error": "blog_id and file are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        blog = Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    # Only author can upload media
    if blog.author != request.user:
        return Response({"error": "You are not allowed to upload media to this blog"}, status=status.HTTP_403_FORBIDDEN)

    media = BlogMedia.objects.create(blog=blog, file=file)
    return Response({"message": "Media uploaded successfully", "media_id": media.id}, status=status.HTTP_201_CREATED)


# Blogs Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def blog_delete_view(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Only author can delete
    if blog.author != request.user:
        return Response({"error": "You are not allowed to delete this blog"}, status=status.HTTP_403_FORBIDDEN)
    
    blog.delete()
    return Response({"message": "Blog deleted successfully"}, status=status.HTTP_200_OK)


# -----------------------------
# CATEGORIES
# -----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list_view(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)



# Category Create
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def category_create_view(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Category Update Delete
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_update_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        category.delete()
        return Response({'message': 'Category deleted'}, status=status.HTTP_204_NO_CONTENT)


# -----------------------------
# REACTIONS
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_reaction(request, blog_id):
    user = request.user
    reaction_type = request.data.get('reaction_type')
    blog = get_object_or_404(Blog, id=blog_id)
    valid_reactions = ['like', 'dislike', 'love', 'laugh', 'angry']
    if reaction_type not in valid_reactions:
        return Response({'error': 'Invalid reaction type'}, status=status.HTTP_400_BAD_REQUEST)

    reaction, created = Reaction.objects.get_or_create(user=user, blog=blog)

    if not created and reaction.reaction_type == reaction_type:
        reaction.delete()
        return Response({'message': 'Reaction removed'})
    else:
        reaction.reaction_type = reaction_type
        reaction.save()
        if blog.author.id != user.id:
            Notification.objects.create(
                user=blog.author,
                sender=user,
                notification_type='reaction',
                blog=blog,
                message=f"{user.username} reacted ({reaction_type}) to your blog '{blog.title}'"
            )
        return Response({'message': f'{reaction_type} added'})
    

# Reactions List
@api_view(['GET'])
@permission_classes([AllowAny])
def reaction_list_view(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    reactions = Reaction.objects.filter(blog=blog)
    serializer = ReactionSerializer(reactions, many=True)
    return Response(serializer.data)

# -----------------------------
# COMMENTS
# -----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def comment_list_view(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    comments = Comment.objects.filter(blog=blog, parent=None)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    content = request.data.get('content')
    if not content:
        return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)

    comment = Comment.objects.create(user=request.user, blog=blog, content=content)

    if blog.author != request.user:
        Notification.objects.create(
            user=blog.author,
            sender=request.user,
            notification_type='comment',
            blog=blog,
            message=f"{request.user.username} commented on your blog"
        )

        # Optional: real-time channels notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{blog.author.id}",
            {
                "type": "send_notification",
                "content": {
                    "message": f"{request.user.username} commented on your blog",
                    "blog_id": blog.id,
                    "notification_type": "comment",
                }
            }
        )

    return Response({"detail": "Comment created successfully."})



# Comment Delete Views
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    comment.delete()
    return Response({'message': 'Comment deleted'}, status=status.HTTP_204_NO_CONTENT)




# -----------------------------
# BOOKMARKS
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_bookmark(request, blog_id):
    user = request.user
    blog = get_object_or_404(Blog, id=blog_id)
    bookmark, created = Bookmark.objects.get_or_create(user=user, blog=blog)
    if not created:
        bookmark.delete()
        return Response({'message': 'Bookmark removed'})
    return Response({'message': 'Bookmark added'})


# User BookMarks
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('blog')
    data = [
        {
            'id': b.blog.id,
            'title': b.blog.title,
            'created_at': b.blog.created_at
        } for b in bookmarks
    ]
    return Response(data)



# -----------------------------
# NOTIFICATIONS
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = [
        {
            "id": n.id,
            "message": n.message,
            "type": n.notification_type,
            "blog_id": n.blog.id if n.blog else None,
            "is_read": n.is_read,
            "created_at": n.created_at
        } for n in notifications
    ]
    return Response(data)


# Notofications Mark Read Views
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def notification_mark_read_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return Response({'message': 'Notification marked as read'})




# -----------------------------
# GENERAL STATS
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_view(request):
    return Response({
        'total_users': CustomUser.objects.count(),
        'total_blogs': Blog.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_reactions': Reaction.objects.count(),
        'total_notifications': Notification.objects.count(),
    })



# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_dashboard(request):
    data = {
        "users": CustomUser.objects.count(),
        "blogs": Blog.objects.count(),
        "comments": Comment.objects.count(),
        "reactions": Reaction.objects.count(),
        "categories": Category.objects.count()
    }
    return Response(data)


# All Users
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def all_users(request):
    users = CustomUser.objects.all()
    data = [clean_user_data(u) for u in users]
    return Response(data)


# Update User Role
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def update_user_role(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    new_role = request.data.get('role')
    if new_role not in ['Admin', 'Editor', 'Author', 'Reader']:
        return Response({'error': 'Invalid role'}, status=400)
    user.role = new_role
    user.save()
    return Response({'status': 'Role updated successfully'})


# Most active Users
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def most_active_users(request):
    users = CustomUser.objects.annotate(activity_count=Count('useractivity')).order_by('-activity_count')[:10]
    data = [clean_user_data(u) for u in users]
    return Response(data)



# Trending Blogs Admin
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def trending_blogs_admin(request):
    blogs = Blog.objects.order_by('-views')[:10]
    serializer = BlogSerializer(blogs, many=True, context={'request': request})
    return Response(serializer.data)
