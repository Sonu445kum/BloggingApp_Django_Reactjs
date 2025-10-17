from rest_framework import serializers
from .models import (
    CustomUser, Profile, Category, Blog, BlogMedia, Comment,
    Reaction, Bookmark, Notification, UserActivity
)
from taggit.serializers import TagListSerializerField, TaggitSerializer
from django.contrib.auth import authenticate

# ====================================
# REGISTER SERIALIZER
# ====================================
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role']  # first_name & last_name removed
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'reader')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# ====================================
# LOGIN SERIALIZER
# ====================================
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Authenticate user using username and password.
        Raises error if credentials are invalid.
        """
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        data['user'] = user
        return data


# ====================================
# CUSTOM USER SERIALIZER (For nested usage)
# ====================================
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'email_verified']  # first_name & last_name removed


# ====================================
# PROFILE SERIALIZER
# ====================================
class ProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    bookmarks_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'bio', 'profile_pic', 'social_links',
            'followers_count', 'following_count', 'bookmarks_count',
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_bookmarks_count(self, obj):
        return obj.bookmarks.count()


# ====================================
# CATEGORY SERIALIZER
# ====================================
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


# ====================================
# BLOG MEDIA SERIALIZER
# ====================================
class BlogMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogMedia
        fields = ['id', 'file', 'uploaded_at']


# ====================================
# COMMENT SERIALIZER (Nested Replies)
# ====================================
class RecursiveCommentSerializer(serializers.Serializer):
    """Recursive serializer for nested comment replies."""
    def to_representation(self, value):
        serializer = CommentSerializer(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    replies = RecursiveCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'parent', 'created_at', 'replies']


# ====================================
# REACTION SERIALIZER
# ====================================
class ReactionSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction_type', 'created_at']


# ====================================
# BOOKMARK SERIALIZER
# ====================================
class BookmarkSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    blog_title = serializers.CharField(source='blog.title', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'blog', 'blog_title', 'created_at']


# ====================================
# BLOG SERIALIZER (Main)
# ====================================
class BlogSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagListSerializerField()
    media = BlogMediaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    bookmarks = BookmarkSerializer(many=True, read_only=True)

    total_reactions = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    total_bookmarks = serializers.SerializerMethodField()
    is_featured_display = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'id', 'author', 'title', 'content', 'markdown_content', 'category',
            'tags', 'featured_image', 'attachments', 'status',
            'views', 'likes', 'comments_count', 'is_featured', 'is_featured_display',
            'publish_at', 'published_at', 'created_at', 'updated_at',
            'media', 'comments', 'reactions', 'bookmarks',
            'total_reactions', 'total_comments', 'total_bookmarks'
        ]

    def get_total_reactions(self, obj):
        return obj.reactions.count()

    def get_total_comments(self, obj):
        return obj.comments.count()

    def get_total_bookmarks(self, obj):
        return obj.bookmarked_by.count() if hasattr(obj, 'bookmarked_by') else 0

    def get_is_featured_display(self, obj):
        return "⭐ Featured" if obj.is_featured else "Normal"


# ====================================
# USER ACTIVITY SERIALIZER
# ====================================
class UserActivitySerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'action', 'timestamp']


# ====================================
# NOTIFICATION SERIALIZER
# ====================================
class NotificationSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
