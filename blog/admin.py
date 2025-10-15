from django.contrib import admin
from .models import CustomUser, Category, Blog, Comment,Like

admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Like)
