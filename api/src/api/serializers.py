from api.models import User
from api.models import TestSession

from rest_framework import serializers
from api.models import (Part3Question, Part1Question, Part1QuestionCategory,Part2Question, UserPart1Result,
                        UserPart2Result, UserPart3Result)
from api.utils.audio_utils import validate_audio_attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'fullname', 'is_active')


class TestSessionSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        error_messages={
            'does_not_exist': 'User with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for user ID, expected integer.'
        }
    )

    class Meta:
        model = TestSession
        fields = ('session_id', 'user_id', 'result', 'created_at', 'updated_at')


class Part1QuestionSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        # queryset=Part1Question.objects.select_related('with_category').all(),
        source='question_category',
        read_only=True,
        slug_field='name',
    )

    class Meta:
        model = Part1Question
        fields = ('id', 'question_txt', 'voice_url', 'category')


class Part2QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part2Question
        fields = ('id', 'question_txt', 'voice_url',)


class Part3QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part3Question
        fields = ('id', 'question_txt', 'voice_url',)


class UserPart1ResultCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Part1Question.objects.all(),
        source='question',
        write_only=True,
        error_messages={
            'does_not_exist': 'Question with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for question ID, expected integer.'
        }
    )

    class Meta:
        model = UserPart1Result
        fields = (
            "user",
            "session",
            "question_id",
            "voice_audio",
        )

    def validate(self, attrs):
        attrs = validate_audio_attrs(attrs)
        return attrs


class UserPart2ResultCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPart2Result
        fields = (
            "id",
            "user",
            "session",
            "question",
            "voice_audio",
        )

    def validate(self, attrs):
        attrs = validate_audio_attrs(attrs)
        return attrs


class UserPart3ResultCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPart3Result
        fields = (
            "id",
            "user",
            "session",
            "question",
            "voice_audio",
        )

    def validate(self, attrs):
        attrs = validate_audio_attrs(attrs)
        return attrs


class TestSessionCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        error_messages={
            'does_not_exist': 'User with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for user ID, expected integer.'
        }
    )

    class Meta:
        model = TestSession
        fields = (
            "user_id",
        )






