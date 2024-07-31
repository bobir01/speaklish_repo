from .models import (Part1Question, Part2Question, Part3Question, SchoolPart1Result, SchoolPart2Result, \
                     SchoolPart3Result, TestSessionSchool, ParsedSession)

from api.serializers import (Part1QuestionSerializer, Part2QuestionSerializer, Part3QuestionSerializer)
from api.utils.audio_utils import validate_audio_attrs

from rest_framework import serializers


class SchoolTestSessionCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    session_id = serializers.IntegerField(required=True)
    referral_code = serializers.CharField(allow_blank=True, allow_null=True)

    part1_questions = Part1QuestionSerializer(many=True, )
    part2_question = Part2QuestionSerializer()
    part3_questions = Part3QuestionSerializer(many=True, )


class SchoolTestSessionResultSerializer(serializers.ModelSerializer):
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=TestSessionSchool.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Session with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for session ID, expected integer.'
        }
    )

    class Meta:
        model = TestSessionSchool
        fields = ('id', 'school_id', 'student_id', 'result', 'stop_reason',
                  'is_test', 'created_at', 'updated_at', 'finished_at'
                  )


class SchoolPart1ResultCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(
        source='question',
        queryset=Part1Question.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Question with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for question ID, expected integer.'
        }
    )
    session_id = serializers.PrimaryKeyRelatedField(
        source='session',
        queryset=TestSessionSchool.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Session with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for session ID, expected integer.'
        }
    )

    class Meta:
        model = SchoolPart1Result
        fields = ('question_id', 'session_id', 'voice_audio',)
        extra_kwargs = {
            'voice_audio': {'required': True}
        }

    def validate(self, attrs):
        question = attrs.get('question')
        session = attrs.get('session')
        validate_audio_attrs(attrs)
        if not SchoolPart1Result.objects.filter(session=session).exists():
            raise serializers.ValidationError('This session does not exist!',
                                              code=400)

        if not SchoolPart1Result.objects.filter(question=question).exists():
            raise serializers.ValidationError('This question is not in this session!',
                                              code=400)
        return attrs


class SchoolPart2ResultCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(
        source='question',
        queryset=Part2Question.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Question with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for question ID, expected integer.'
        }
    )
    session_id = serializers.PrimaryKeyRelatedField(
        source='session',
        queryset=TestSessionSchool.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Session with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for session ID, expected integer.'
        }
    )

    class Meta:
        model = SchoolPart2Result
        fields = ('question_id', 'session_id', 'voice_audio',)
        extra_kwargs = {
            'voice_audio': {'required': True}
        }

    def validate(self, attrs):
        question = attrs.get('question')
        session = attrs.get('session')
        validate_audio_attrs(attrs)  # base validation on audio file for size, extension
        if not SchoolPart2Result.objects.filter(session=session).exists():
            raise serializers.ValidationError('This session does not exist!')

        if not SchoolPart2Result.objects.filter(question=question, session=session).exists():
            raise serializers.ValidationError('This question is not in this session!')
        return attrs


class SchoolPart3ResultCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(
        source='question',
        queryset=Part3Question.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Question with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for question ID, expected integer.'
        }
    )
    session_id = serializers.PrimaryKeyRelatedField(
        source='session',
        queryset=TestSessionSchool.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Session with ID {pk_value} does not exist.',
            'incorrect_type': 'Incorrect type for session ID, expected integer.'
        }
    )

    class Meta:
        model = SchoolPart2Result
        fields = ('question_id', 'session_id', 'voice_audio',)
        extra_kwargs = {
            'voice_audio': {'required': True}
        }

    def validate(self, attrs):
        question = attrs.get('question')
        session = attrs.get('session')
        validate_audio_attrs(attrs)
        if not SchoolPart3Result.objects.filter(session=session).exists():
            raise serializers.ValidationError('This session does not exist!')

        if not SchoolPart3Result.objects.filter(question=question, session=session).exists():
            raise serializers.ValidationError('This question is not in this session!')

        return attrs


class ParsedSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedSession
        fields = ('id',
                  'session',
                  'raw_json',
                  'parsed_json',
                  'feedback',
                  'band_score',
                  'fluency',
                  'vocabulary',
                  'grammar',
                  'pronunciation',
                  'used_topic_words',
                  'suggested_vocab',
                  'token_usage',
                  'wait_time',
                  'created_at')

    def create(self, validated_data):
        score = self.initial_data['score']
        data = {'band_score': (score['band']),
                'fluency': (score['fluency']),
                'vocabulary': (score['vocabulary']),
                'grammar': (score['grammar']),
                'pronunciation': (score['pronunciation']),
                }

        return ParsedSession.objects.create(**validated_data,
                                            **data)


class DefaultResponseSerializer(serializers.Serializer):
    msg = serializers.CharField(required=True, max_length=255, allow_blank=False, allow_null=False)
    ok = serializers.BooleanField(default=True)
