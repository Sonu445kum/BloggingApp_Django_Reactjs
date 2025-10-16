from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from taggit.models import Tag

from .models import (
    CustomUser, Profile, Category, Blog, BlogMedia, Comment,
    Reaction, Notification, UserActivity, Bookmark
)
from .serializers import (
    CustomUserSerializer, ProfileSerializer, CategorySerializer, BlogSerializer,
    BlogMediaSerializer, CommentSerializer, ReactionSerializer,
    NotificationSerializer, RegisterSerializer
)
from .utils import profile_completion

# Alias for backward compatibility
UserSerializer = CustomUserSerializer

# -----------------------------
# UTILS
# -----------------------------
def send_notification_to_user(user_id, message):
    """
    Send a real-time notification via Django Channels
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {"type": "send_notification", "message": {"message": message}}
    )


def send_verification_email(user, request):
    """
    Send verification email to the user
    """
    token = RefreshToken.for_user(user).access_token
    current_site = get_current_site(request).domain
    relative_link = reverse('verify-email')
    absurl = f"http://{current_site}{relative_link}?token={str(token)}"
    email_body = f"Hi {user.username},\n\nUse the link below to verify your email:\n{absurl}"
    send_mail(
        'Verify your email',
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )

# -----------------------------
# TAG SUGGESTIONS
# -----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def tag_suggestions(request):
    """Autocomplete tag suggestions based on user input"""
    q = request.query_params.get('q', '').strip()
    if not q:
        return Response([])
    tags = Tag.objects.filter(name__istartswith=q).values_list('name', flat=True)[:10]
    return Response(list(tags))


# -----------------------------
# USER ACTIVITY LOGS
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_logs(request):
    """Return the logged-in user's activity logs"""
    logs = UserActivity.objects.filter(user=request.user).order_by('-timestamp')
    data = [{"action": log.action, "time": log.timestamp} for log in logs]
    return Response(data)


# -----------------------------
# PROFILE COMPLETION
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_status(request):
    """Return user's profile completion percentage"""
    user = request.user
    completion = profile_completion(user)
    return Response({"profile_completion": completion})


# -----------------------------
# AUTHENTICATION
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user and send email verification"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        send_verification_email(user, request)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Return current logged-in user details"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify user's email using the token"""
    token = request.GET.get('token')
    try:
        payload = AccessToken(token)
        user = CustomUser.objects.get(id=payload['user_id'])
        if not user.email_verified:
            user.email_verified = True
            user.save()
        return Response({'message': 'Email successfully verified'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# PASSWORD RESET / CHANGE
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Send a password reset email to the user"""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'No user found with this email'}, status=status.HTTP_404_NOT_FOUND)

    token = PasswordResetTokenGenerator().make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/reset-password/?uid={user.id}&token={token}"

    send_mail(
        'Password Reset Request',
        f'Click the link to reset your password: {reset_url}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    return Response({'message': 'Password reset link sent to email'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset user password using token"""
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    if not uid or not token or not new_password:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(id=uid)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid user'}, status=status.HTTP_404_NOT_FOUND)

    if not PasswordResetTokenGenerator().check_token(user, token):
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password for logged-in user"""
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
# BLOG CRUD
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def blog_create_view(request):
    """Create a new blog"""
    serializer = BlogSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def blog_update_view(request, pk):
    """Update a blog created by the user"""
    blog = get_object_or_404(Blog, pk=pk)
    if blog.author != request.user:
        return Response({'error': "You cannot edit someone else's blog"}, status=status.HTTP_403_FORBIDDEN)
    serializer = BlogSerializer(blog, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def blog_list_view(request):
    """List published blogs with optional filters: search, category, tag, author"""
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def draft_blogs_view(request):
    """Return all draft blogs of the logged-in user"""
    drafts = Blog.objects.filter(author=request.user, status='draft').order_by('-created_at')
    serializer = BlogSerializer(drafts, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def blog_detail_view(request, pk):
    """Return details of a single blog"""
    blog = get_object_or_404(Blog, pk=pk)
    serializer = BlogSerializer(blog, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def trending_blogs_view(request):
    """Return top trending blogs (by views)"""
    blogs = Blog.objects.filter(status='published').order_by('-views')[:10]
    serializer = BlogSerializer(blogs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def blog_media_upload_view(request):
    """Upload media (image/video) for blogs"""
    serializer = BlogMediaSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# CATEGORIES
# -----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list_view(request):
    """List all categories"""
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def category_create_view(request):
    """Create a new category"""
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_update_delete_view(request, pk):
    """Update or delete a category"""
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

# Toggle Reactions view 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_reaction(request, blog_id):
    """
    Add/remove reaction to a blog and notify the author in real-time.
    - If user adds a new reaction, creates/updates it.
    - If same reaction exists, removes it.
    - Sends notification to blog author if someone else reacts.
    """
    user = request.user
    reaction_type = request.data.get('reaction_type')
    blog = get_object_or_404(Blog, id=blog_id)

    valid_reactions = ['like', 'dislike', 'love', 'laugh', 'angry']
    if reaction_type not in valid_reactions:
        return Response({'error': 'Invalid reaction type'}, status=status.HTTP_400_BAD_REQUEST)

    # Get or create reaction
    reaction, created = Reaction.objects.get_or_create(user=user, blog=blog)

    if not created and reaction.reaction_type == reaction_type:
        # Same reaction exists, remove it
        reaction.delete()
        return Response({'message': 'Reaction removed'})
    else:
        # Add/update reaction
        reaction.reaction_type = reaction_type
        reaction.save()

        # Notify blog author if reacting user is not the author
        if blog.author.id != user.id:
            # Create Notification object
            Notification.objects.create(
                user=blog.author,
                sender=user,
                notification_type='reaction',
                blog=blog,
                message=f"{user.username} reacted ({reaction_type}) to your blog '{blog.title}'"
            )

            # Send real-time notification via WebSocket
            send_notification_to_user(
                user_id=blog.author.id,
                message=f"{user.username} reacted ({reaction_type}) to your blog '{blog.title}'",
                notification_type='reaction',
                blog_id=blog.id
            )

        return Response({'message': f'{reaction_type} added'})


@api_view(['GET'])
@permission_classes([AllowAny])
def reaction_list_view(request, blog_id):
    """List all reactions for a blog"""
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
    """List all comments (top-level) for a blog"""
    blog = get_object_or_404(Blog, pk=blog_id)
    comments = Comment.objects.filter(blog=blog, parent=None)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


# -----------------------------
# COMMENTS
# -----------------------------
from webpush import send_user_notification  # Add this import at the top with other imports
from django.core.mail import send_mail       # Add this import too

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, blog_id):
    """Add a comment (or reply) to a blog and notify the author (DB + WebSocket + Web Push + Email)"""
    blog = get_object_or_404(Blog, id=blog_id)
    
    # 1️ Create the comment
    comment = Comment.objects.create(
        user=request.user,
        blog=blog,
        content=request.data.get('content')
    )

    # 2️ Create DB notification for blog author (if not commenting on own blog)
    if blog.author != request.user:
        Notification.objects.create(
            user=blog.author,
            sender=request.user,
            notification_type='comment',
            blog=blog,
            message=f"{request.user.username} commented on your blog"
        )

        # 3️ Send Email notification
        if blog.author.email:
            send_mail(
                subject="New Comment on Your Blog",
                message=f"{request.user.username} commented on your blog.",
                from_email="noreply@yourdomain.com",
                recipient_list=[blog.author.email],
            )

        # 4️ Real-time notification via Channels (WebSocket)
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

        # 5 Web push notification
        payload = {
            "head": "New Comment!",
            "body": f"{request.user.username} commented on your blog.",  # Updated as per your request
            "icon": "/static/images/comment-icon.png",  # Optional
            "url": f"/blogs/{blog.id}/"                 # Optional: URL user can open
        }
        send_user_notification(user=blog.author, payload=payload, ttl=1000)

    return Response({"detail": "Comment created successfully."})



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete_view(request, pk):
    """Delete a comment if user is the owner"""
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
    """Add/remove a bookmark for a blog"""
    user = request.user
    blog = get_object_or_404(Blog, id=blog_id)
    bookmark, created = Bookmark.objects.get_or_create(user=user, blog=blog)
    if not created:
        bookmark.delete()
        return Response({'message': 'Bookmark removed'})
    return Response({'message': 'Bookmark added'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmarks(request):
    """List all bookmarks of logged-in user"""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('blog')
    data = [{'id': b.blog.id, 'title': b.blog.title, 'created_at': b.blog.created_at} for b in bookmarks]
    return Response(data)


# -----------------------------
# -----------------------------
# NOTIFICATIONS
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notifications(request):
    """
    List all notifications for the logged-in user in reverse chronological order.
    Each notification includes:
    - id
    - message
    - type (comment, reaction, announcement)
    - related blog id (if any)
    - read/unread status
    - creation timestamp
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = [
        {
            "id": n.id,
            "message": n.message,
            "type": n.notification_type,
            "blog_id": n.blog.id if n.blog else None,
            "is_read": n.is_read,
            "created_at": n.created_at
        }
        for n in notifications
    ]
    return Response(data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def notification_mark_read_view(request, pk):
    """
    Mark a specific notification as read.
    Only the owner of the notification can mark it as read.
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return Response({'message': 'Notification marked as read'})



# -----------------------------
# ADMIN STATS
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_view(request):
    """Return admin dashboard statistics"""
    return Response({
        'total_users': CustomUser.objects.count(),
        'total_blogs': Blog.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_reactions': Reaction.objects.count(),
        'total_notifications': Notification.objects.count(),
    })
