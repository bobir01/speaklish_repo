from rest_framework import serializers
from api.models import Part1Question, Part2Question, Part3Question


class QuestionsPart1QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part1Question
        fields = ('id', 'question_txt', 'voice_url', 'question_category')
        read_only_fields = ('voice_url',)


class QuestionsPart2QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part2Question
        fields = ('id', 'question_txt', 'voice_url',)
        read_only_fields = ('voice_url',)


class QuestionsPart3QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part3Question
        fields = ('id', 'part2_question', 'question_txt', 'voice_url',)
        read_only_fields = ('voice_url',)


class QuestionTTSInputSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, min_length=10, max_length=1000)
    part_number = serializers.IntegerField(required=False)
    id_ = serializers.IntegerField(required=False)
    lang = serializers.ChoiceField(choices=['en', 'ru'], default='en')
    gender = serializers.ChoiceField(choices=['female', 'male'], default='female')


    def validate(self, attrs):
        gender = attrs.get('gender').lower()

        if gender not in ('female', 'male'):
            raise serializers.ValidationError
        if attrs.get('lang') not in ('en', 'ru'):
            raise serializers.ValidationError
        return attrs
