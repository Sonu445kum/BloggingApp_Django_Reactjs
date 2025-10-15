from django.contrib import admin
from .models import CustomUser, Category, Blog, Comment

admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Blog)
admin.site.register(Comment)
