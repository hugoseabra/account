from django.contrib import admin

from .models import Avatar


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ('image', 'type', 'main', 'user')
    list_filter = ('user', 'type', 'main',)
    search_fields = ('image',)
