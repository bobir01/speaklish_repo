import uuid
import random

from django.db import models
from django.contrib.auth.models import AbstractUser, User as DjangoUser
from django.db.models import Max
from django.conf import settings


class User(models.Model):
    fullname = models.CharField(max_length=255, blank=True, null=True, db_column='fullname')
    username = models.CharField(max_length=255, null=True, db_column='username',
                                unique=True)
    user_id = models.BigIntegerField(blank=True, db_column='user_id')
    is_active = models.BooleanField(default=True, db_column='is_active')
    referral = models.CharField(max_length=255, blank=True, null=True, db_column='referral')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username or self.fullname or self.user_id


class TestSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False,
                                  unique=True,
                                  db_column='session_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='test_sessions',
                             db_column='user_id')
    result = models.TextField(blank=True, null=True, db_column='result')
    part1_question = models.IntegerField(blank=True, null=True, db_column='part1_question_id')

    # finish state is choice field as part1, part2, part3  or null

    finish_state = models.CharField(max_length=255, blank=True, null=True, db_column='finish_state')
    stop_reason = models.CharField(max_length=255, blank=True, null=True, db_column='stop_reason')
    model_name = models.CharField(max_length=255, blank=True, null=True, db_column='model_name')
    wait_time = models.IntegerField(blank=True, null=True, db_column='wait_time',
                                    db_comment='wait time in request in seconds')
    used_tokens = models.IntegerField(blank=True, null=True, db_column='used_tokens')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'test_sessions'
        verbose_name = 'Test-Session'
        verbose_name_plural = 'Test-Sessions'

    def get_part1_question(self):
        return Part1Question.objects.get(id=self.part1_question)

    def __str__(self):
        return str(self.session_id)


class Part1QuestionCategory(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, db_column='name')
    is_active = models.BooleanField(default=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'part1_question_categories'
        verbose_name = 'Part-1 Question Category'
        verbose_name_plural = 'Part-1 Question Categories'

    def __str__(self):
        return f'{self.id}. {self.name}'


class Part1Question(models.Model):
    question_txt = models.TextField(blank=True, db_column='question')
    question_category = models.ForeignKey(Part1QuestionCategory, blank=True,
                                          db_column='question_category_id',
                                          related_name='with_category',
                                          on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, blank=True)
    voice_url = models.URLField(blank=True, null=True, db_column='voice_url')
    # topic = models.CharField(max_length=255, blank=True, null=True, db_column='topic')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'Part1: {self.id}-{self.question_txt}'

    class Meta:
        db_table = 'part1_questions'
        verbose_name = 'Part-1 Question'
        verbose_name_plural = 'Part-1 Questions'

    @classmethod
    def get_random_question(cls, is_test=False):
        active_qs = Part1QuestionCategory.objects.filter(is_active=True)
        if active_qs.exists():
            if settings.IN_TEST or is_test:
                return 5
            return random.choice(active_qs)
        #     return cls.objects.filter(question_category_id=random_id).order_by('id').all()
        return None


class UserPart1Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, db_column='session_id',
                                related_name='user_part1_results',
                                related_query_name='user_part1_result')
    question = models.ForeignKey(Part1Question, on_delete=models.CASCADE, db_column='question_id',
                                 related_name='part1_questions',
                                 related_query_name='part1_question')
    answer = models.TextField(blank=True, null=True, )
    tts_name = models.CharField(max_length=100, blank=True, null=True, db_column='tts_name')
    voice_audio = models.FileField(upload_to='voices', null=True, db_column='voice_audio')
    answer_voice_id = models.CharField(max_length=255, blank=True, null=True, db_column='answer_voice_id',
                                       db_comment='voice id from from telegram voice message file_id')
    voice_length = models.IntegerField(blank=True, null=True, db_column='length',
                                       db_comment='length of answer in seconds')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'Part1 results: {self.id}-{self.user}'

    class Meta:
        db_table = 'user_part1_results'
        verbose_name = 'UserPart1Result'
        verbose_name_plural = 'UserPart1Results'


class Part2Question(models.Model):
    question_txt = models.TextField(blank=True, db_column='question')
    voice_url = models.URLField(blank=True, null=True, db_column='voice_url')
    is_active = models.BooleanField(default=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'Part2: {self.id}-{self.question_txt[:50]}'

    class Meta:
        db_table = 'part2_questions'
        verbose_name = 'Part-2 Question'
        verbose_name_plural = 'Part-2 Questions'

    @classmethod
    def get_random_question(cls, is_test=False):
        active_questions = cls.objects.filter(is_active=True)
        if active_questions.exists():
            if settings.IN_TEST or is_test:
                return cls.objects.get(pk=3)
            return random.choice(active_questions)
        return None


class UserPart2Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, db_column='session_id',
                                related_name='user_part2_results',
                                related_query_name='user_part2_result')
    question = models.ForeignKey(Part2Question, on_delete=models.CASCADE, db_column='question_id', null=True,
                                 related_name='part2_questions',
                                 related_query_name='part2_question')
    answer = models.TextField(blank=True, null=True, )
    voice_audio = models.FileField(upload_to='voices', null=True, db_column='voice_audio')
    tts_name = models.CharField(max_length=100, blank=True, null=True, db_column='tts_name')
    answer_voice_id = models.CharField(max_length=255, blank=True, null=True, db_column='answer_voice_id',
                                       db_comment='voice id from from telegram voice message file_id')
    voice_length = models.IntegerField(blank=True, null=True, db_column='length',
                                       db_comment='length of answer in seconds')
    tts_process_time = models.IntegerField(blank=True, null=True, db_column='tts_process_time',
                                           db_comment='wait time in request in seconds')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'Part2 results: {self.id}-{self.user}'

    class Meta:
        db_table = 'user_part2_results'
        verbose_name = 'UserPart2Result'
        verbose_name_plural = 'UserPart2Results'


class Part3Question(models.Model):
    question_txt = models.TextField(blank=True, db_column='question_txt')
    part2_question = models.ForeignKey(Part2Question, on_delete=models.CASCADE,
                                       db_column='part2_question_id')
    is_active = models.BooleanField(default=True, blank=True)
    voice_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'Part3: {self.id}-{self.question_txt}'

    class Meta:
        db_table = 'part3_questions'
        verbose_name = 'Part-3 Question'
        verbose_name_plural = 'Part-3 Questions'


class UserPart3Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, db_column='session_id',
                                related_name='user_part3_results',
                                related_query_name='user_part3_result')
    question = models.ForeignKey(Part3Question, on_delete=models.CASCADE, db_column='question_id',
                                 null=True,
                                 related_name='part3_questions',
                                 related_query_name='part3_question')
    answer = models.TextField(blank=True, null=True)
    tts_name = models.CharField(max_length=100, blank=True, null=True, db_column='tts_name')
    answer_voice_id = models.CharField(max_length=255, blank=True, null=True, db_column='answer_voice_id',
                                       db_comment='voice id from from telegram voice message file_id')
    voice_audio = models.FileField(upload_to='voices', null=True, db_column='voice_audio')
    voice_length = models.IntegerField(blank=True, null=True, db_column='length',
                                       db_comment='length of answer in seconds')
    tts_process_time = models.IntegerField(blank=True, null=True, db_column='tts_process_time',
                                           db_comment='wait time in request in seconds')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'user_part3_results'
        verbose_name = 'UserPart3Result'
        verbose_name_plural = 'UserPart3Results'

    def __str__(self):
        return f'P3 results: {self.id}-{self.user}'
