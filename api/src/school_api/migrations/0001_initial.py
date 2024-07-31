# Generated by Django 4.2.9 on 2024-03-24 10:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestSessionSchool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.TextField(blank=True, db_column='result', null=True)),
                ('student_id', models.BigIntegerField(db_column='student_id', null=True)),
                ('finish_state', models.CharField(blank=True, db_column='finish_state', max_length=255, null=True)),
                ('stop_reason', models.CharField(blank=True, db_column='stop_reason', max_length=255, null=True)),
                ('model_name', models.CharField(blank=True, db_column='model_name', max_length=255, null=True)),
                ('wait_time', models.IntegerField(blank=True, db_column='wait_time', db_comment='wait time in request in seconds', null=True)),
                ('used_tokens', models.IntegerField(blank=True, db_column='used_tokens', null=True)),
                ('is_test', models.BooleanField(blank=True, db_column='is_test', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('school', models.ForeignKey(db_column='school_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_schools', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Test-Session School',
                'verbose_name_plural': 'Test-Session Schools',
                'db_table': 'test_session_schools',
            },
        ),
        migrations.CreateModel(
            name='SchoolProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_name', models.CharField(db_column='school_name', max_length=255, null=True)),
                ('session_count', models.IntegerField(db_column='session_count', default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('school', models.OneToOneField(db_column='school_id', on_delete=django.db.models.deletion.CASCADE, related_name='school_profiles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'School Profile',
                'verbose_name_plural': 'School Profiles',
                'db_table': 'school_profiles',
            },
        ),
        migrations.CreateModel(
            name='SchoolPart3Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(blank=True, db_column='answer', null=True)),
                ('tts_name', models.CharField(blank=True, db_column='tts_name', max_length=255, null=True)),
                ('answer_voice_id', models.CharField(blank=True, db_column='answer_voice_id', help_text='voice id from telegram file id', max_length=255, null=True)),
                ('voice_audio', models.FileField(db_column='voice_audio', null=True, upload_to='part3/')),
                ('voice_length', models.IntegerField(blank=True, db_column='voice_length', null=True)),
                ('status', models.CharField(blank=True, choices=[('pending', 'pending'), ('completed', 'completed'), ('failed', 'failed')], db_column='status', db_comment='status of the result', help_text='pending, completed, failed', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('question', models.ForeignKey(db_column='question_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_questions_part3', to='api.part3question')),
                ('school', models.ForeignKey(db_column='school_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_schools_part3', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(db_column='session_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_sessions_part3', to='school_api.testsessionschool')),
            ],
            options={
                'verbose_name': 'School Part3 Result',
                'verbose_name_plural': 'School Part3 Results',
                'db_table': 'school_part3_results',
            },
        ),
        migrations.CreateModel(
            name='SchoolPart2Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(blank=True, db_column='answer', null=True)),
                ('tts_name', models.CharField(blank=True, db_column='tts_name', max_length=255, null=True)),
                ('answer_voice_id', models.CharField(blank=True, db_column='answer_voice_id', help_text='voice id from telegram file id', max_length=255, null=True)),
                ('voice_audio', models.FileField(db_column='voice_audio', null=True, upload_to='part2/')),
                ('voice_length', models.IntegerField(blank=True, db_column='voice_length', null=True)),
                ('status', models.CharField(blank=True, choices=[('pending', 'pending'), ('completed', 'completed'), ('failed', 'failed')], db_column='status', db_comment='status of the result', help_text='pending, completed, failed', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('question', models.ForeignKey(db_column='question_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_questions_part2', to='api.part2question')),
                ('school', models.ForeignKey(db_column='school_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_schools_part2', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(db_column='session_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_sessions_part2', to='school_api.testsessionschool')),
            ],
            options={
                'verbose_name': 'School Part2 Result',
                'verbose_name_plural': 'School Part2 Results',
                'db_table': 'school_part2_results',
            },
        ),
        migrations.CreateModel(
            name='SchoolPart1Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(blank=True, db_column='answer', null=True)),
                ('tts_name', models.CharField(blank=True, db_column='tts_name', max_length=255, null=True)),
                ('answer_voice_id', models.CharField(blank=True, db_column='answer_voice_id', help_text='voice id from telegram file id', max_length=255, null=True)),
                ('voice_audio', models.FileField(db_column='voice_audio', null=True, upload_to='part1/')),
                ('voice_length', models.IntegerField(blank=True, db_column='voice_length', null=True)),
                ('status', models.CharField(blank=True, choices=[('pending', 'pending'), ('completed', 'completed'), ('failed', 'failed')], db_column='status', db_comment='status of the result', help_text='pending, completed, failed', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('question', models.ForeignKey(db_column='question_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_questions_part1', to='api.part1question')),
                ('school', models.ForeignKey(db_column='school_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_schools_part1', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(db_column='session_id', on_delete=django.db.models.deletion.CASCADE, related_name='with_sessions_part1', to='school_api.testsessionschool')),
            ],
            options={
                'verbose_name': 'School Part1 Result',
                'verbose_name_plural': 'School Part1 Results',
                'db_table': 'school_part1_results',
            },
        ),
    ]