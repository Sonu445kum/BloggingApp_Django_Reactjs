from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import CustomUser, Blog, Category, Comment
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    BlogSerializer,
    CategorySerializer,
    CommentSerializer,
)

# --------------------------
# User Registration
# --------------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------------------
# Get current user info
# --------------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_detail_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# --------------------------
# Blog CRUD
# --------------------------
@api_view(['GET', 'POST'])
def blog_list_create_view(request):
    if request.method == 'GET':
        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def blog_detail_view(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return Response({'detail': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)

    # GET
    if request.method == 'GET':
        serializer = BlogSerializer(blog)
        return Response(serializer.data)

    # PUT
    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user != blog.author and not request.user.is_admin:
            return Response({'detail': 'You cannot edit this blog'}, status=status.HTTP_403_FORBIDDEN)

        serializer = BlogSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user != blog.author and not request.user.is_admin:
            return Response({'detail': 'You cannot delete this blog'}, status=status.HTTP_403_FORBIDDEN)

        blog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------
# Category APIs (Admin only)
# --------------------------
@api_view(['GET', 'POST'])
def category_list_create_view(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_staff:
            return Response({'detail': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------------------
# Comment APIs
# --------------------------
@api_view(['GET', 'POST'])
def comment_list_create_view(request, blog_id):
    if request.method == 'GET':
        comments = Comment.objects.filter(blog_id=blog_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, blog_id=blog_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
