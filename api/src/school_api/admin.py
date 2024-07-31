from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, mark_safe, escape

from school_api.models import (TestSessionSchool, SchoolProfile, SchoolPart1Result,
                               SchoolPart2Result, SchoolPart3Result,
                               ParsedSession, SchoolReferralQuestionSet, PronunciationResult)

from school_api.utils.admin_commands import reprocess_session


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'school_username', 'school_name', 'session_count', 'created_at', 'updated_at')

    list_display_links = ('school_name',)

    search_fields = ('school_name',)


@admin.register(SchoolPart1Result)
class SchoolPart1ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'school_id', 'session_id', 'question', 'tts_name', 'answer_voice_id',
                    'voice_audio', 'created_at', 'finished_at', 'updated_at')
    list_filter = ('created_at', 'finished_at')
    list_display_links = ('question',)

    search_fields = ('session__id',)
    ordering = ('id',)


@admin.register(SchoolPart2Result)
class SchoolPart2ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'school_id', 'session_id', 'question', 'tts_name', 'answer_voice_id',
                    'voice_audio', 'created_at', 'finished_at', 'updated_at')
    list_filter = ('created_at', 'finished_at')
    list_display_links = ('question',)

    search_fields = ('session__id',)
    ordering = ('id',)


@admin.register(SchoolPart3Result)
class SchoolPart3ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'school_id', 'session_id', 'question', 'tts_name', 'answer_voice_id',
                    'voice_audio', 'created_at', 'finished_at', 'updated_at')
    list_filter = ('created_at', 'finished_at')
    list_display_links = ('question',)

    search_fields = ('session__id',)
    ordering = ('id',)


@admin.register(ParsedSession)
class ParsedSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'band_score', 'token_usage', 'created_at')
    list_filter = ('created_at', 'band_score', 'token_usage')
    list_display_links = ('session',)

    search_fields = ('band_score', 'session__id')
    ordering = ('id',)


class SchoolPart1ResultInline(admin.TabularInline):
    model = SchoolPart1Result
    extra = 0
    can_delete = False
    readonly_fields = [field.name for field in SchoolPart1Result._meta.fields]

    def has_change_permission(self, request, obj=None):
        return False


class SchoolPart2ResultInline(admin.TabularInline):
    model = SchoolPart2Result
    extra = 0
    can_delete = False
    readonly_fields = [field.name for field in SchoolPart2Result._meta.fields]

    def has_change_permission(self, request, obj=None):
        return False


class SchoolPart3ResultInline(admin.TabularInline):
    model = SchoolPart3Result
    extra = 0
    can_delete = False
    readonly_fields = [field.name for field in SchoolPart3Result._meta.fields]

    def has_change_permission(self, request, obj=None):
        return False


class ParsedSessionInline(admin.TabularInline):
    model = ParsedSession
    extra = 0
    can_delete = False
    readonly_fields = [field.name for field in ParsedSession._meta.fields]

    def has_change_permission(self, request, obj=None):
        return False


class PronunciationResultInline(admin.TabularInline):
    model = PronunciationResult
    extra = 0
    can_delete = False
    readonly_fields = [field.name for field in PronunciationResult._meta.fields]

    def has_change_permission(self, request, obj=None):
        return False



@admin.register(TestSessionSchool)
class TestSessionSchoolAdmin(admin.ModelAdmin):
    inlines = [
        SchoolPart1ResultInline,
        SchoolPart2ResultInline,
        SchoolPart3ResultInline,
        PronunciationResultInline,
        ParsedSessionInline,
    ]
    actions = [reprocess_session]

    list_display = (
        'id', 'school_id', 'finish_state', 'student_id', 'is_test', 'send_message_view', 'created_at', 'updated_at')
    list_filter = ('is_test', 'finish_state', 'created_at', 'updated_at')
    list_display_links = ('student_id',)

    search_fields = ('id', 'student_id')
    ordering = ('id',)

    def send_message_view(self, obj):
        user_id = obj.student_id
        link = reverse('school-send-message') + f'?user_id={user_id}'
        return format_html(f'<a href="{link}">Send ✉️</a>')


# lets add tabular inline for part1, part2, part3 questions
class Part1QuestionCategoryInline(admin.TabularInline):
    model = SchoolReferralQuestionSet.part1_category.through
    extra = 0
    can_delete = False


class Part2QuestionInline(admin.TabularInline):
    model = SchoolReferralQuestionSet.part2_questions.through
    extra = 0
    can_delete = False


@admin.register(SchoolReferralQuestionSet)
class SchoolReferralQuestionSetAdmin(admin.ModelAdmin):
    list_display = ('school', 'referral_name', 'created_at', 'updated_at')
    search_fields = ('school__username', 'referral_name')
    filter_horizontal = ('part1_category', 'part2_questions',)
    exclude = ('part1_questions', 'part3_questions')
    inlines = [
        Part1QuestionCategoryInline,
        Part2QuestionInline,
    ]
