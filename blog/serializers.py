# from rest_framework import serializers
# from .models import (
#     CustomUser, Profile, Category, Blog, BlogMedia, Comment,
#     Reaction, Bookmark, Notification, UserActivity
# )
# from taggit.serializers import TagListSerializerField, TaggitSerializer
# from django.contrib.auth import authenticate
# from .models import CustomUser

# # ====================================
# # REGISTER SERIALIZER
# # ====================================
# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'password', 'role']  # first_name & last_name removed
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = CustomUser(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             role=validated_data.get('role', 'reader')
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user


# # ====================================
# # LOGIN SERIALIZER
# # ====================================
# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         username = attrs.get("username")
#         password = attrs.get("password")

#         if username and password:
#             user = authenticate(username=username, password=password)
#             if not user:
#                 raise serializers.ValidationError("Invalid credentials.")
#             if not user.is_active:
#                 raise serializers.ValidationError("Please verify your email before logging in.")
#             attrs['user'] = user
#             return attrs
#         raise serializers.ValidationError("Both username and password are required.")

# # ====================================
# # CUSTOM USER SERIALIZER (For nested usage)
# # ====================================
# class CustomUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'role', 'email_verified']  # first_name & last_name removed


# class ProfileSerializer(serializers.ModelSerializer):
#     user = CustomUserSerializer(read_only=True)
#     followers_count = serializers.SerializerMethodField()
#     following_count = serializers.SerializerMethodField()
#     bookmarks_count = serializers.SerializerMethodField()

#     class Meta:
#         model = Profile
#         fields = [
#             'id', 'user', 'bio', 'profile_pic', 'social_links',
#             'followers_count', 'following_count', 'bookmarks_count',
#         ]

#     def get_followers_count(self, obj):
#         return obj.followers.count()

#     def get_following_count(self, obj):
#         return obj.following.count()

#     def get_bookmarks_count(self, obj):
#         return obj.bookmarks.count()



# # ====================================
# # CATEGORY SERIALIZER
# # ====================================
# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'slug']


# # ====================================
# # BLOG MEDIA SERIALIZER
# # ====================================
# class BlogMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BlogMedia
#         fields = ['id', 'file', 'uploaded_at']


# # ====================================
# # COMMENT SERIALIZER (Nested Replies)
# # ====================================
# class RecursiveCommentSerializer(serializers.Serializer):
#     """Recursive serializer for nested comment replies."""
#     def to_representation(self, value):
#         serializer = CommentSerializer(value, context=self.context)
#         return serializer.data


# class CommentSerializer(serializers.ModelSerializer):
#     user = CustomUserSerializer(read_only=True)
#     replies = RecursiveCommentSerializer(many=True, read_only=True)

#     class Meta:
#         model = Comment
#         fields = ['id', 'user', 'content', 'parent', 'created_at', 'replies']



# # ====================================
# # BOOKMARK SERIALIZER
# # ====================================
# class BookmarkSerializer(serializers.ModelSerializer):
#     user = CustomUserSerializer(read_only=True)
#     blog_title = serializers.CharField(source='blog.title', read_only=True)

#     class Meta:
#         model = Bookmark
#         fields = ['id', 'user', 'blog', 'blog_title', 'created_at']


# # ====================================
# # BLOG SERIALIZER (Main)
# # ====================================
# class BlogSerializer(TaggitSerializer, serializers.ModelSerializer):
#     author = CustomUserSerializer(read_only=True)
#     category = CategorySerializer(read_only=True)
#     tags = TagListSerializerField()
#     media = BlogMediaSerializer(many=True, read_only=True)
#     comments = CommentSerializer(many=True, read_only=True)
#     reactions = ReactionSerializer(many=True, read_only=True)
#     bookmarks = BookmarkSerializer(many=True, read_only=True)

#     total_reactions = serializers.SerializerMethodField()
#     total_comments = serializers.SerializerMethodField()
#     total_bookmarks = serializers.SerializerMethodField()
#     is_featured_display = serializers.SerializerMethodField()

#     class Meta:
#         model = Blog
#         fields = [
#             'id', 'author', 'title', 'content', 'markdown_content', 'category',
#             'tags', 'featured_image', 'attachments', 'status',
#             'views', 'likes', 'comments_count', 'is_featured', 'is_featured_display',
#             'publish_at', 'published_at', 'created_at', 'updated_at',
#             'media', 'comments', 'reactions', 'bookmarks',
#             'total_reactions', 'total_comments', 'total_bookmarks'
#         ]

#     def get_total_reactions(self, obj):
#         return obj.reactions.count()

#     def get_total_comments(self, obj):
#         return obj.comments.count()

#     def get_total_bookmarks(self, obj):
#         return obj.bookmarked_by.count() if hasattr(obj, 'bookmarked_by') else 0

#     def get_is_featured_display(self, obj):
#         return "⭐ Featured" if obj.is_featured else "Normal"
    

# # ====================================
# # REACTION SERIALIZER
# # ====================================
# class ReactionSerializer(serializers.ModelSerializer):
#     user = CustomUserSerializer(read_only=True)
#     blog = BlogSerializer(read_only=True)  # include blog info

#     class Meta:
#         model = Reaction
#         fields = ['id', 'user', 'blog', 'reaction_type', 'created_at']



# # ====================================
# # USER ACTIVITY SERIALIZER
# # ====================================
# class UserActivitySerializer(serializers.ModelSerializer):
#     user = CustomUserSerializer(read_only=True)

#     class Meta:
#         model = UserActivity
#         fields = ['id', 'user', 'action', 'timestamp']


# # ====================================
# # NOTIFICATION SERIALIZER
# # ====================================
# class NotificationSerializer(serializers.ModelSerializer):
#     #  Receiver (notification target user)
#     user = CustomUserSerializer(read_only=True)
    
#     #  Sender (who triggered the notification)
#     sender = CustomUserSerializer(read_only=True)
    
#     #  Optional: include blog info if attached
#     blog = BlogSerializer(read_only=True)

#     class Meta:
#         model = Notification
#         fields = [
#             'id',
#             'user',
#             'sender',
#             'notification_type',
#             'blog',
#             'message',
#             'is_read',
#             'created_at'
#         ]


# backend/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from taggit.serializers import TagListSerializerField, TaggitSerializer

from .models import (
    CustomUser, Profile, Category, Blog, BlogMedia, Comment,
    Reaction, Bookmark, Notification, UserActivity
)

# ====================================
# REGISTER SERIALIZER
# ====================================
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role']
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
# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         username = attrs.get("username")
#         password = attrs.get("password")

#         if username and password:
#             user = authenticate(username=username, password=password)
#             if not user:
#                 raise serializers.ValidationError("Invalid credentials.")
#             if not user.is_active:
#                 raise serializers.ValidationError("Please verify your email before logging in.")
#             attrs['user'] = user
#             return attrs
#         raise serializers.ValidationError("Both username and password are required.")

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get("username")
        password = attrs.get("password")

        if not username_or_email or not password:
            raise serializers.ValidationError("Both username/email and password are required.")

        # Try authenticating with username first
        user = authenticate(username=username_or_email, password=password)

        # If not authenticated, try using email
        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid username/email or password.")

        if not user:
            raise serializers.ValidationError("Invalid username/email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Please verify your email before logging in.")

        attrs['user'] = user
        return attrs



# ====================================
# CUSTOM USER SERIALIZER
# ====================================
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'email_verified']


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
    file = serializers.SerializerMethodField()

    class Meta:
        model = BlogMedia
        fields = ['id', 'file', 'uploaded_at']

    def get_file(self, obj):
        """Return absolute URL for image file"""
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None


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
# BOOKMARK SERIALIZER
# ====================================
class BookmarkSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    blog_title = serializers.CharField(source='blog.title', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'blog', 'blog_title', 'created_at']


# # ====================================
# # BLOG SERIALIZER (UPDATED)
# # ====================================
# class BlogSerializer(TaggitSerializer, serializers.ModelSerializer):
#     author = CustomUserSerializer(read_only=True)
#     category = CategorySerializer(read_only=True)
#     tags = TagListSerializerField(required=False)
#     media = BlogMediaSerializer(many=True, read_only=True)
#     comments = CommentSerializer(many=True, read_only=True)
#     reactions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#     bookmarks = BookmarkSerializer(many=True, read_only=True)

#     total_reactions = serializers.SerializerMethodField()
#     total_comments = serializers.SerializerMethodField()
#     total_bookmarks = serializers.SerializerMethodField()
#     is_featured_display = serializers.SerializerMethodField()

#     class Meta:
#         model = Blog
#         fields = [
#             'id', 'author', 'title', 'content', 'markdown_content', 'category',
#             'tags', 'featured_image', 'attachments', 'status',
#             'views', 'likes', 'comments_count', 'is_featured', 'is_featured_display',
#             'publish_at', 'published_at', 'created_at', 'updated_at',
#             'media', 'comments', 'reactions', 'bookmarks',
#             'total_reactions', 'total_comments', 'total_bookmarks'
#         ]

#     # ✅ Add absolute URLs for featured_image & attachments
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         request = self.context.get('request')

#         if request:
#             # ✅ Convert featured_image to absolute URL if available
#             if instance.featured_image:
#                 try:
#                     data['featured_image'] = request.build_absolute_uri(instance.featured_image.url)
#                 except Exception:
#                     data['featured_image'] = None

#             # ✅ Convert attachments to absolute URL (if exists)
#             if instance.attachments:
#                 try:
#                     data['attachments'] = request.build_absolute_uri(instance.attachments.url)
#                 except Exception:
#                     data['attachments'] = None

#         return data

#     # ✅ Helper Methods
#     def get_total_reactions(self, obj):
#         return obj.reactions.count()

#     def get_total_comments(self, obj):
#         return obj.comments.count()

#     def get_total_bookmarks(self, obj):
#         return obj.bookmarked_by.count() if hasattr(obj, 'bookmarked_by') else 0

#     def get_is_featured_display(self, obj):
#         return "⭐ Featured" if obj.is_featured else "Normal"


# ====================================
# BLOG SERIALIZER (FINAL UPDATED ✅)
# ====================================
class BlogSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    media = BlogMediaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    reactions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    bookmarks = BookmarkSerializer(many=True, read_only=True)

    total_reactions = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    total_bookmarks = serializers.SerializerMethodField()
    is_featured_display = serializers.SerializerMethodField()

    # ✅ New fields for emoji reactions
    reaction_summary = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'id', 'author', 'title', 'content', 'markdown_content', 'category',
            'tags', 'featured_image', 'attachments', 'status',
            'views', 'likes', 'comments_count', 'is_featured', 'is_featured_display',
            'publish_at', 'published_at', 'created_at', 'updated_at',
            'media', 'comments', 'reactions', 'bookmarks',
            'total_reactions', 'total_comments', 'total_bookmarks',
            # 👇 newly added fields
            'reaction_summary', 'user_reaction',
        ]

    # ✅ Convert media paths to absolute URLs
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request:
            # ✅ Convert featured_image to absolute URL
            if instance.featured_image:
                try:
                    data['featured_image'] = request.build_absolute_uri(instance.featured_image.url)
                except Exception:
                    data['featured_image'] = None

            # ✅ Convert attachments to absolute URL
            if instance.attachments:
                try:
                    data['attachments'] = request.build_absolute_uri(instance.attachments.url)
                except Exception:
                    data['attachments'] = None

        return data

    # ✅ Helper Methods
    def get_total_reactions(self, obj):
        return obj.reactions.count()

    def get_total_comments(self, obj):
        return obj.comments.count()

    def get_total_bookmarks(self, obj):
        return obj.bookmarked_by.count() if hasattr(obj, 'bookmarked_by') else 0

    def get_is_featured_display(self, obj):
        return "⭐ Featured" if obj.is_featured else "Normal"

    # ✅ Get summarized emoji reaction counts
    def get_reaction_summary(self, obj):
        summary = {'like': 0, 'love': 0, 'laugh': 0, 'angry': 0}
        for r in obj.reactions.all():
            summary[r.reaction_type] = summary.get(r.reaction_type, 0) + 1
        return summary

    # ✅ Get current user's reaction type (if any)
    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            return reaction.reaction_type if reaction else None
        return None




# ====================================
# REACTION SERIALIZER
# ====================================
class ReactionSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    blog = BlogSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'blog', 'reaction_type', 'created_at']


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
    user = CustomUserSerializer(read_only=True)  # receiver
    sender = CustomUserSerializer(read_only=True)  # sender
    blog = BlogSerializer(read_only=True)  # optional attached blog

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'sender',
            'notification_type',
            'blog',
            'message',
            'is_read',
            'created_at'
        ]