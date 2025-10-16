from rest_framework import serializers
from .models import (
    CustomUser,
    Profile,
    Category,
    Blog,
    BlogMedia,
    Comment,
    Reaction,
    Notification
)
from taggit.serializers import (TagListSerializerField, TaggitSerializer)

# ----------------------------
# REGISTER SERIALIZER
# ----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'author')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# ----------------------------
# USER SERIALIZER
# ----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'email_verified']

# ----------------------------
# PROFILE SERIALIZER
# ----------------------------
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'profile_pic', 'social_links', 'following', 'bookmarks']

# ----------------------------
# CATEGORY SERIALIZER
# ----------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

# ----------------------------
# BLOG MEDIA SERIALIZER
# ----------------------------
class BlogMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogMedia
        fields = ['id', 'file', 'uploaded_at']

# ----------------------------
# BLOG SERIALIZER
# ----------------------------
class BlogSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField()
    category = CategorySerializer(read_only=True)
    media = BlogMediaSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'id', 'author', 'title', 'content', 'markdown_content', 'status', 'category',
            'tags', 'featured_image', 'attachments', 'media', 'views', 'likes', 'comments_count',
            'publish_at', 'published_at', 'created_at', 'updated_at', 'reactions_count', 'is_featured'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_reactions_count(self, obj):
        return obj.reactions.count()

# ----------------------------
# TRENDING BLOG SERIALIZER
# ----------------------------
class TrendingBlogSerializer(BlogSerializer):
    pass  # reuse fields from BlogSerializer

# ----------------------------
# COMMENT SERIALIZER
# ----------------------------
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'blog', 'parent', 'content', 'created_at', 'updated_at', 'replies']

    def get_replies(self, obj):
        return CommentSerializer(obj.replies.all(), many=True).data

# ----------------------------
# REACTION SERIALIZER
# ----------------------------
class ReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'blog', 'type', 'created_at']

# ----------------------------
# NOTIFICATION SERIALIZER
# ----------------------------
class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
