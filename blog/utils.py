from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

def send_verification_email(user, request):
    token = RefreshToken.for_user(user).access_token
    current_site = get_current_site(request).domain
    relative_link = reverse('email-verify')  # we will create this route
    absurl = f"http://{current_site}{relative_link}?token={str(token)}"
    email_body = f"Hi {user.username}, Use the link below to verify your email:\n{absurl}"
    send_mail(
        'Verify your email',
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )


# Profiles Completions
def profile_completion(user):
    fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture', 'phone']
    total_fields = len(fields)
    filled_fields = sum(1 for field in fields if getattr(user, field))
    completion_percentage = int(filled_fields / total_fields * 100)
    return completion_percentage
