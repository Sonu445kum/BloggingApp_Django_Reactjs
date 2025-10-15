from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# -------------------------
# Root view
# -------------------------
def root_view(request):
    """
    Handles the root URL '/'.
    Returns a simple JSON message for testing the API.
    In production, you can redirect this to the React frontend.
    """
    return JsonResponse({"message": "Welcome to the Blogging Platform API"})

# -------------------------
# URL patterns
# -------------------------
urlpatterns = [
    path('', root_view),  # Root URL
    path('admin/', admin.site.urls),  # Admin panel
    path('api/', include('blog.urls')),  # Include blog app APIs

    # JWT authentication endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# -------------------------
# Serve media files during development
# -------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
