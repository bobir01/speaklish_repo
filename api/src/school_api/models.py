import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, User as DjangoUser
from api.models import Part1Question, Part2Question, Part3Question


class SchoolProfile(models.Model):
    school_name = models.CharField(max_length=255, null=True, db_column='school_name')
    school = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, db_column='school_id',
                                  related_name='school_profiles')
    session_count = models.IntegerField(default=0, db_column='session_count')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def school_username(self):
        return self.school.username

    def __str__(self):
        return self.school_name

    class Meta:
        db_table = 'school_profiles'
        verbose_name = 'School Profile'
        verbose_name_plural = 'School Profiles'


status_choices = [
    ('pending', 'pending'),
    ('completed', 'completed'),
    ('failed', 'failed')
]


class TestSessionSchool(models.Model):
    school = models.ForeignKey(DjangoUser, on_delete=models.CASCADE,
                               related_name='with_schools',
                               db_column='school_id')
    result = models.TextField(blank=True, null=True, db_column='result')
    student_id = models.BigIntegerField(blank=False, null=True, db_column='student_id')
    # finish state is choice field as part1, part2, part3  or null

    finish_state = models.CharField(max_length=255, blank=True, null=True, db_column='finish_state')
    stop_reason = models.CharField(max_length=255, blank=True, null=True, db_column='stop_reason')
    model_name = models.CharField(max_length=255, blank=True, null=True, db_column='model_name')
    wait_time = models.IntegerField(blank=True, null=True, db_column='wait_time',
                                    db_comment='wait time in request in seconds')
    used_tokens = models.IntegerField(blank=True, null=True, db_column='used_tokens')
    is_test = models.BooleanField(null=True, blank=True, db_column='is_test')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'test_session_schools'
        verbose_name = 'Test-Session School'
        verbose_name_plural = 'Test-Session Schools'

    def __str__(self):
        if self.finish_state:
            return f'School: {self.school}|id:{self.id} - {self.finish_state}'
        if self.result is not None:
            return f'School: {self.school}|id:{self.id} - Completed'

        return f'School: {self.school}|id:{self.id} - {self.finish_state}'


class SchoolPart1Result(models.Model):
    school = models.ForeignKey(DjangoUser, on_delete=models.CASCADE,
                               related_name='with_schools_part1',
                               db_column='school_id')
    session = models.ForeignKey(TestSessionSchool, on_delete=models.CASCADE,
                                related_name='with_sessions_part1',
                                db_column='session_id')
    question = models.ForeignKey(Part1Question, on_delete=models.CASCADE,
                                 related_name='with_questions_part1',
                                 db_column='question_id')
    answer = models.TextField(blank=True, null=True, db_column='answer')
    tts_name = models.CharField(max_length=255, blank=True, null=True, db_column='tts_name')
    answer_voice_id = models.CharField(max_length=255, blank=True, null=True, db_column='answer_voice_id',
                                       help_text='voice id from telegram file id')
    voice_audio = models.FileField(upload_to='part1/', blank=False, null=True, db_column='voice_audio')
    voice_length = models.IntegerField(blank=True, null=True, db_column='voice_length')
    status = models.CharField(max_length=255, choices=status_choices, db_column='status', null=True, blank=True,
                              help_text='pending, completed, failed', db_comment='status of the result')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'school_part1_results'
        verbose_name = 'School Part1 Result'
        verbose_name_plural = 'School Part1 Results'


class SchoolPart2Result(models.Model):
    school = models.ForeignKey(DjangoUser, on_delete=models.CASCADE,
                               related_name='with_schools_part2',
                               db_column='school_id')
    session = models.ForeignKey(TestSessionSchool, on_delete=models.CASCADE,
                                related_name='with_sessions_part2',
                                db_column='session_id')
    question = models.ForeignKey(Part2Question, on_delete=models.CASCADE,
                                 related_name='with_questions_part2',
                                 db_column='question_id')
    answer = models.TextField(blank=True, null=True, db_column='answer')
    tts_name = models.CharField(max_length=255, blank=True, null=True, db_column='tts_name')
    answer_voice_id = models.CharField(max_length=255, blank=True, null=True, db_column='answer_voice_id',
                                       help_text='voice id from telegram file id')
    voice_audio = models.FileField(upload_to='part2/', null=True, db_column='voice_audio')
    voice_length = models.IntegerField(blank=True, null=True, db_column='voice_length')
    status = models.CharField(max_length=255, choices=status_choices, db_column='status', null=True, blank=True,
                              help_text='pending, completed, failed', db_comment='status of the result')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'school_part2_results'
        verbose_name = 'School Part2 Result'
        verbose_name_plural = 'School Part2 Results'


class SchoolPart3Result(models.Model):
    school = models.ForeignKey(DjangoUser, on_delete=models.CASCADE,
                               related_name='with_schools_part3',
                               db_column='school_id')
    session = models.ForeignKey(TestSessionSchool, on_delete=models.CASCADE,
                                related_name='with_sessions_part3',
                                db_column='session_id')
    question = models.ForeignKey(Part3Question, on_delete=models.CASCADE,
                                 related_name='with_questions_part3',
                                 db_column='question_id')
    answer = models.TextField(blank=True, null=True, db_column='answer')
    tts_name = models.CharField(max_length=255, blank=True, null=True, db_column='tts_name')
    answer_voice_id = models.CharField(max_length=255, blank=True, null=True, db_column='answer_voice_id',
                                       help_text='voice id from telegram file id')
    voice_audio = models.FileField(upload_to='part3/', null=True, db_column='voice_audio')
    voice_length = models.IntegerField(blank=True, null=True, db_column='voice_length')
    status = models.CharField(max_length=255, choices=status_choices, db_column='status', null=True, blank=True,
                              help_text='pending, completed, failed', db_comment='status of the result')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'school_part3_results'
        verbose_name = 'School Part3 Result'
        verbose_name_plural = 'School Part3 Results'

    def __str__(self):
        return f'Session-part3: {self.session}|id:{self.id} - {self.status}'


class ParsedSession(models.Model):
    session = models.ForeignKey(TestSessionSchool, on_delete=models.CASCADE, related_name='parsed_sessions')
    raw_json = models.TextField()
    parsed_json = models.JSONField()
    feedback = models.TextField(blank=True)
    band_score = models.DecimalField(blank=True, max_digits=2, decimal_places=1)
    fluency = models.DecimalField(blank=True, max_digits=2, decimal_places=1)
    vocabulary = models.DecimalField(blank=True, max_digits=2, decimal_places=1)
    grammar = models.DecimalField(blank=True, max_digits=2, decimal_places=1)
    pronunciation = models.DecimalField(blank=True, null=True, max_digits=2, decimal_places=1)
    used_topic_words = models.JSONField()
    suggested_vocab = models.JSONField()
    wait_time = models.FloatField(blank=True)
    token_usage = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'parsed_sessions'
        verbose_name = 'Parsed Session'
        verbose_name_plural = 'Parsed Sessions'

    def __str__(self):
        return f'{self.session} - {self.band_score}'


class SchoolReferralQuestionSet(models.Model):
    school = models.ForeignKey(DjangoUser, on_delete=models.CASCADE, related_name='referral_question_sets')
    referral_name = models.CharField(max_length=255, null=True, blank=True)
    part1_category = models.ManyToManyField('api.Part1QuestionCategory', related_name='referral_part1_categories')
    part2_questions = models.ManyToManyField(Part2Question, related_name='referral_part2_questions')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'school_referral_question_sets'
        verbose_name = 'School Referral Question Set'
        verbose_name_plural = 'School Referral Question Sets'

    def __str__(self):
        return f'{self.school}'


class PronunciationResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(TestSessionSchool,
                                on_delete=models.SET_NULL,
                                related_name='pronunciation_results', null=True)
    score = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    score_details = models.JSONField(null=True)
    time_taken = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
