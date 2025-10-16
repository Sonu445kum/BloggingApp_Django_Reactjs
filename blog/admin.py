from django.contrib import admin
from .models import (
    CustomUser,
    Profile,
    Category,
    Blog,
    Comment,
    Reaction,
    Notification
)

# Simple direct registrations (best for function-based view projects)
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(Notification)
