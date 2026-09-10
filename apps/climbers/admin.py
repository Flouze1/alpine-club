from django.contrib import admin
from .models import climbers, groups, climber_members


@admin.register(climbers)
class ClimberAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'sports_category', 'schoole', 'test']
    list_filter = ['sports_category', 'schoole', 'test']
    search_fields = ['last_name', 'first_name', 'email']


@admin.register(groups)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'mountain_id', 'max_members', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']


@admin.register(climber_members)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['climber_id', 'groups_id', 'role', 'joined_date']
    list_filter = ['role', 'joined_date']
    search_fields = ['climber_id__last_name']