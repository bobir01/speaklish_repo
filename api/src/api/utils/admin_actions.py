from django.db import models


# action for admin panel
def toggle_active(modeladmin, request, queryset):
    """Toggle active status of the selected objects."""
    for obj in queryset:
        obj.is_active = not obj.is_active
        obj.save()