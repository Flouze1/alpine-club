from django.contrib import admin
from .models import mountains


@admin.register(mountains)
class MountainAdmin(admin.ModelAdmin):
    list_display = ['name', 'height', 'country', 'difficulty']
    list_filter = ['country', 'difficulty']
    search_fields = ['name', 'country']