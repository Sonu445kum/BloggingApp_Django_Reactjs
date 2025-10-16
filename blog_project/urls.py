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
    Returns a simple JSON message to verify the API is running.
    """
    return JsonResponse({"message": "Welcome to the Blogging Platform API"})

# -------------------------
# URL patterns
# -------------------------
urlpatterns = [
    # Root URL
    path('', root_view, name='root'),  # API root endpoint

    # Django admin panel
    path('admin/', admin.site.urls),

    # Social authentication (Google, Facebook, GitHub via Django Allauth)
    path('accounts/', include('allauth.urls')),

    # Blog app API endpoints
    path('api/', include('blog.urls')),  # Include all URLs from the 'blog' app

    # JWT authentication endpoints
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Get JWT token
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),      # Refresh JWT token
]

# -------------------------
# Serve media files during development
# -------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
