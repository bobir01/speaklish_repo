import logging

from rest_framework import serializers
from writing_checker.utils.docs_service import docx_to_text, get_pdf_text, count_words
from .models import Task1Essay, Task2Essay


class WritingTask1CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task1Essay
        fields = [
            'student_id',
            'essay',
            'topic',
            'graph_image',
            'document'
        ]
        extra_kwargs = {
            'document': {
                'write_only': True,
                'required': False
            },
            'essay': {
                'write_only': True,
                'required': False
            }
        }

    def validate(self, attrs):
        if not attrs.get('essay') and not attrs.get('document'):
            raise serializers.ValidationError('Either essay or document is required')

        if attrs.get('essay') and attrs.get('document'):
            raise serializers.ValidationError('Either essay or document is required, not both')

        if attrs.get('document').name.split('.')[-1] not in ['docx', 'pdf']:
            raise serializers.ValidationError('Only docx and pdf files are allowed')

        return attrs

    def create(self, validated_data):
        essay = validated_data.get('essay')
        document = validated_data.get('document')
        if document:
            if document.name.split('.')[-1] == 'pdf':
                text = get_pdf_text(document)
            else:
                text = docx_to_text(document)
            validated_data['essay'] = text
        if essay:
            validated_data['essay'] = essay
        logging.info(f'validated_data: {validated_data}')
        validated_data['word_count'] = count_words(validated_data['essay'])

        return Task1Essay.objects.create(**validated_data)


class ScoreSerializer(serializers.Serializer):
    band_score = serializers.FloatField()
    task_response = serializers.FloatField()
    coherence_cohesion = serializers.FloatField()
    lexical_resource = serializers.FloatField()
    grammatical_accuracy = serializers.FloatField()


class WritingTask1ResponseSerializer(serializers.ModelSerializer):
    # score_ = ScoreSerializer()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Task1Essay
        fields = [
            'id',
            'score',
            'feedback',
            'student_id',
            'wait_time',
            'graph_image',
            'word_count',
        ]

    def get_score(self, obj):
        json_response = obj.prompt_json[-1].get('content')[0].get('text')
        return {
            'band_score': json_response.get('band_score', 0),
            'task_response': json_response.get('task_response', 0),
            'coherence_cohesion': json_response.get('coherence_cohesion', 0),
            'lexical_resource': json_response.get('lexical_resource', 0),
            'grammatical_accuracy': json_response.get('grammatical_accuracy', 0),
        }


class WritingTask2CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task2Essay
        fields = [
            'essay',
            'student_id',
            'topic',
            'document'
        ]
        extra_kwargs = {
            'document': {
                'write_only': True,
                'required': False
            },
            'essay': {
                'write_only': True,
                'required': False
            }
        }

    def validate(self, attrs):
        if not attrs.get('essay') and not attrs.get('document'):
            raise serializers.ValidationError('Either essay or document is required')

        if attrs.get('essay') and attrs.get('document'):
            raise serializers.ValidationError('Either essay or document is required, not both')

        if attrs.get('document').name.split('.')[-1] not in ['docx', 'pdf']:
            raise serializers.ValidationError('Only docx and pdf files are allowed')

        return attrs

    def create(self, validated_data):
        essay = validated_data.get('essay')
        document = validated_data.get('document')
        if document:
            if document.name.split('.')[-1] == 'pdf':
                text = get_pdf_text(document)
            else:
                text = docx_to_text(document)
            validated_data['essay'] = text
        if essay:
            validated_data['essay'] = essay
        logging.info(f'validated_data: {validated_data}')
        validated_data['word_count'] = count_words(validated_data['essay'])

        return Task2Essay.objects.create(**validated_data)


class WritingTask2ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task2Essay
        fields = [
            'id',
            'score',
            'feedback',
            'student_id',
            'topic',
            'word_count',
            'created_at',
        ]
