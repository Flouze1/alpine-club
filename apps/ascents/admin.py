from django.contrib import admin
from .models import climbs


@admin.register(climbs)
class AscentAdmin(admin.ModelAdmin):
    list_display = ['group_id', 'start_event', 'result', 'note']
    list_filter = ['result', 'start_event']
    search_fields = ['group_id__name', 'comment']
    date_hierarchy = 'start_event'