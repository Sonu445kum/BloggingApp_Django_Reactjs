from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken

from .models import CustomUser, Profile, Category, Blog, Comment, Reaction, Notification
from .serializers import (
    UserSerializer, ProfileSerializer, CategorySerializer, BlogSerializer,
    CommentSerializer, ReactionSerializer, NotificationSerializer, RegisterSerializer
)
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# ----------------------------
# REQUEST PASSWORD RESET
# ----------------------------
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
    
    token = PasswordResetTokenGenerator().make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/reset-password/?uid={user.id}&token={token}"

    # Email send karna (simple)
    send_mail(
        subject='Password Reset Request',
        message=f'Click the link to reset your password: {reset_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    
    return Response({'message': 'Password reset link sent to email'}, status=status.HTTP_200_OK)


# ----------------------------
# RESET PASSWORD
# ----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
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


# ----------------------------
# CHANGE PASSWORD (AUTHENTICATED)
# ----------------------------
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

# ----------------------------
# UTILS
# ----------------------------
def send_verification_email(user, request):
    token = RefreshToken.for_user(user).access_token
    current_site = get_current_site(request).domain
    relative_link = reverse('email-verify')  # this route will be added in urls.py
    absurl = f"http://{current_site}{relative_link}?token={str(token)}"
    email_body = f"Hi {user.username},\nUse the link below to verify your email:\n{absurl}"
    send_mail(
        'Verify your email',
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )

# ----------------------------
# EMAIL VERIFICATION
# ----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
    token = request.GET.get('token')
    try:
        payload = AccessToken(token)
        user = CustomUser.objects.get(id=payload['user_id'])
        if not user.email_verified:
            user.email_verified = True
            user.save()
        return Response({'message': 'Email successfully verified'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------
# AUTH
# ----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        send_verification_email(user, request)  # <-- send verification email
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# ----------------------------
# BLOGS
# ----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def blog_list_view(request):
    blogs = Blog.objects.all().order_by('-created_at')
    serializer = BlogSerializer(blogs, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def blog_detail_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    
    if request.method == 'GET':
        blog.views += 1
        blog.save()
        serializer = BlogSerializer(blog)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if blog.author != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BlogSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if blog.author != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        blog.delete()
        return Response({'message': 'Blog deleted'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def blog_create_view(request):
    serializer = BlogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def blog_update_delete_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    
    if blog.author != request.user:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = BlogSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        blog.delete()
        return Response({'message': 'Blog deleted'}, status=status.HTTP_204_NO_CONTENT)

# ----------------------------
# CATEGORIES
# ----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list_view(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def category_create_view(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

# ----------------------------
# COMMENTS
# ----------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def comment_list_view(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    comments = Comment.objects.filter(blog=blog, parent=None)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create_view(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    data = request.data.copy()
    data['blog'] = blog.id
    serializer = CommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    comment.delete()
    return Response({'message': 'Comment deleted'}, status=status.HTTP_204_NO_CONTENT)

# ----------------------------
# REACTIONS
# ----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reaction_toggle_view(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    reaction_type = request.data.get('type')
    
    if reaction_type not in ['like', 'love', 'wow']:
        return Response({'error': 'Invalid reaction type'}, status=status.HTTP_400_BAD_REQUEST)
    
    reaction, created = Reaction.objects.get_or_create(user=request.user, blog=blog)
    if not created:
        if reaction.type == reaction_type:
            reaction.delete()
            return Response({'message': 'Reaction removed'})
        else:
            reaction.type = reaction_type
            reaction.save()
            return Response({'message': 'Reaction updated'})
    else:
        reaction.type = reaction_type
        reaction.save()
        return Response({'message': 'Reaction added'})

@api_view(['GET'])
@permission_classes([AllowAny])
def reaction_list_view(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    reactions = Reaction.objects.filter(blog=blog)
    serializer = ReactionSerializer(reactions, many=True)
    return Response(serializer.data)

# ----------------------------
# NOTIFICATIONS
# ----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def notification_mark_read_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return Response({'message': 'Notification marked as read'})

# ----------------------------
# ADMIN STATS (OPTIONAL)
# ----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_view(request):
    total_users = CustomUser.objects.count()
    total_blogs = Blog.objects.count()
    total_comments = Comment.objects.count()
    total_reactions = Reaction.objects.count()
    total_notifications = Notification.objects.count()

    return Response({
        'total_users': total_users,
        'total_blogs': total_blogs,
        'total_comments': total_comments,
        'total_reactions': total_reactions,
        'total_notifications': total_notifications,
    })
