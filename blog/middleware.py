# blog_project/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import UserActivity

class UserActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            UserActivity.objects.create(user=request.user, action=f"Visited {request.path}")
