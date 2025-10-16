from rest_framework import serializers
from .models import (
    CustomUser,
    Profile,
    Category,
    Blog,
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
            role=validated_data.get('role', 'user')  # default role user
        )
        user.set_password(validated_data['password'])  # hash password
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
# BLOG SERIALIZER
# ----------------------------
class BlogSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField()  # for taggit integration
    category = CategorySerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'id', 'author', 'title', 'content', 'status', 'category',
            'tags', 'featured_image', 'attachments', 'views',
            'publish_at', 'created_at', 'updated_at',
            'comments_count', 'reactions_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_reactions_count(self, obj):
        return obj.reactions.count()


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
