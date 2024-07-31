from django.db import models
from school_api.tasks import process_feedback_task
# django messages
from django.contrib import messages


# action for admin panel
def reprocess_session(modeladmin, request, queryset):
    """Reprocess session."""
    for session in queryset:
        session.finish_state = 'reprocessing'
        session.save()
        process_feedback_task.delay(session_id_pk=session.id)
        messages.success(request, f'Session: {session.id} reprocessing started')
