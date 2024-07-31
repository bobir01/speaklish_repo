from django.contrib import admin
from api.utils.admin_actions import toggle_active
from .models import Part1Question, Part2Question, Part3Question, Part1QuestionCategory  # noqa


@admin.register(Part1QuestionCategory)
class Part1QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    list_display_links = ('name',)
    search_fields = ('name',)
    ordering = ('id',)
    actions = [toggle_active]


@admin.register(Part1Question)
class Part1QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_category', 'question_txt', 'is_active', 'voice_url', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    list_display_links = ('question_txt',)
    search_fields = ('question_txt', 'question_category__name')
    ordering = ('question_category_id', 'id',)
    actions = [toggle_active]


@admin.register(Part2Question)
class Part2QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_txt', 'voice_url', 'is_active', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    list_display_links = ('question_txt',)
    search_fields = ('question_txt',)
    ordering = ('id',)
    actions = [toggle_active]


@admin.register(Part3Question)
class Part3QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_txt', 'part2_question', 'is_active', 'voice_url', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    list_display_links = ('question_txt',)
    search_fields = ('question_txt',)
    ordering = ('part2_question__id', 'id',)
    actions = [toggle_active]
