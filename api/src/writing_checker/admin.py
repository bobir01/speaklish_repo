from django.contrib import admin
from writing_checker.models import WritingConfig, Task1Essay, Task2Essay


@admin.register(WritingConfig)
class WritingConfigAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'temp', 'max_tokens', 'system_text']


@admin.register(Task1Essay)
class Task1EssayAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'topic', 'score', 'word_count', 'created_at']
    search_fields = ['student_id', 'topic']
    list_filter = ['created_at', 'score']


@admin.register(Task2Essay)
class Task2EssayAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'topic', 'score', 'word_count', 'created_at']
    search_fields = ['student_id', 'topic']
    list_filter = ['created_at', 'score']