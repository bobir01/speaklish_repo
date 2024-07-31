from django.db import models


class WritingConfig(models.Model):
    model_name = models.CharField(max_length=255,
                                  choices=(('gpt-4o', 'GPT4-O'),
                                           ('gpt-4-turbo', 'GPT4-Turbo'),
                                           ('mixtral', 'MIXTRAL')),
                                  default='gpt4-o')
    temp = models.FloatField(default=0)
    max_tokens = models.IntegerField(default=1000)
    system_text = models.TextField(null=True)

    @staticmethod
    def get_config():
        config = WritingConfig.objects.get(pk=1)
        return config



class Task1Essay(models.Model):
    essay = models.TextField(null=True)
    is_checked = models.BooleanField(default=False)
    is_passed = models.BooleanField(default=False)
    score = models.FloatField(null=True)
    feedback = models.TextField(null=True)
    student_id = models.BigIntegerField()
    model = models.CharField(max_length=255, null=True)
    topic = models.CharField(max_length=500, null=True)
    prompt_json = models.JSONField(null=True)
    wait_time = models.FloatField(null=True)
    token_usage = models.IntegerField(null=True)
    graph_image = models.URLField(null=True)
    word_count = models.IntegerField(null=True)
    document = models.FileField(upload_to='task1_essay/', null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task1_essays'
        verbose_name = 'Task 1 Essay'
        verbose_name_plural = 'Task 1 Essays'

    def __str__(self):
        return f'Task1Essay {self.id}'


class Task2Essay(models.Model):
    essay = models.TextField(null=True)
    is_checked = models.BooleanField(default=False)
    is_passed = models.BooleanField(default=False)
    score = models.FloatField(null=True)
    feedback = models.TextField(null=True)
    student_id = models.BigIntegerField()
    model = models.CharField(max_length=255, null=True)
    topic = models.CharField(max_length=500, null=True)
    prompt_json = models.JSONField(null=True)
    wait_time = models.FloatField(null=True)
    token_usage = models.IntegerField(null=True)
    word_count = models.IntegerField(null=True)
    document = models.FileField(upload_to='task2_essay/', null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task2_essays'
        verbose_name = 'Task 2 Essay'
        verbose_name_plural = 'Task 2 Essays'

    def __str__(self):
        return f'Task2Essay {self.id}'
