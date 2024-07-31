import logging

from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

from django.conf import settings
from .utils import generate_audio

from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
)

from api.models import (
    Part1Question,
    Part2Question,
    Part3Question,
    Part1QuestionCategory
)
from .serializers import (
    QuestionsPart1QuestionSerializer,
    QuestionsPart2QuestionSerializer,
    QuestionsPart3QuestionSerializer, QuestionTTSInputSerializer
)
from .forms import (
    Part1QuestionForm,
    Part2QuestionForm,
    Part3QuestionForm,
    LoginForm
)


class Part1QuestionListAPIView(ListAPIView):
    queryset = Part1Question.objects.all()
    serializer_class = QuestionsPart1QuestionSerializer


class Part1QuestionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Part1Question.objects.all()
    serializer_class = QuestionsPart1QuestionSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        generate_audio(instance.id, instance.question_txt, 1)

    def perform_destroy(self, instance):
        file_path = os.path.join(settings.MEDIA_ROOT, 'part1', f'question_{instance.id}.mp3')
        if os.path.exists(file_path):
            os.remove(file_path)
        instance.delete()


class Part1QuestionCreateAPIView(CreateAPIView):
    serializer_class = QuestionsPart1QuestionSerializer

    def post(self, request, format=None):
        serializer = QuestionsPart1QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()
            audio_file_path = generate_audio(question.id, question.question_txt, 1)
            question.voice_url = audio_file_path
            question.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def list_questions(request):
    questions = Part1Question.objects.all()
    serializer = QuestionsPart1QuestionSerializer(questions, many=True)
    return Response(serializer.data)


class QuestionListView(View):
    def get(self, request):
        questions = Part1Question.objects.all()
        return render(request, 'questions_list.html', {'questions': questions})


def create_question(request):
    if request.method == 'POST':
        serializer = QuestionsPart1QuestionSerializer(data=request.POST)
        if serializer.is_valid():
            question = serializer.save()
            audio_file_path = generate_audio(question.id, question.question_txt, 1)
            question.voice_url = audio_file_path
            question.save()
            return redirect('list_questions')
    else:
        form = Part1QuestionForm()
    return render(request, 'create_question.html', {'form': form})


class Part2QuestionListAPIView(ListAPIView):
    queryset = Part2Question.objects.all()
    serializer_class = QuestionsPart2QuestionSerializer


class Part2QuestionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Part2Question.objects.all()
    serializer_class = QuestionsPart2QuestionSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        generate_audio(instance.id, instance.question_txt, 2)


class Part2QuestionCreateAPIView(CreateAPIView):
    serializer_class = QuestionsPart2QuestionSerializer

    def post(self, request, format=None):
        serializer = QuestionsPart2QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()
            audio_file_path = generate_audio(question.id, question.question_txt, 2)
            question.voice_url = audio_file_path
            question.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Part3QuestionListAPIView(ListAPIView):
    queryset = Part3Question.objects.all()
    serializer_class = QuestionsPart3QuestionSerializer


class Part3QuestionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Part3Question.objects.all()
    serializer_class = QuestionsPart3QuestionSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        generate_audio(instance.id, instance.question_txt, 3)


class Part3QuestionCreateAPIView(CreateAPIView):
    serializer_class = QuestionsPart3QuestionSerializer

    def post(self, request, format=None):
        serializer = QuestionsPart3QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()
            audio_file_path = generate_audio(question.id, question.question_txt, 3)
            question.voice_url = audio_file_path
            question.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('create_question', part='part1')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'questions/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


class CreateQuestionView(View):
    def get(self, request, part):
        if part == 'part1':
            categories = Part1QuestionCategory.objects.all()
            return render(request, 'questions/create_question.html', {'part': part, 'categories': categories})
        elif part == 'part3':
            part2_questions = Part2Question.objects.all()
            return render(request, 'questions/create_question.html', {'part': part, 'part2_questions': part2_questions})
        else:
            return render(request, 'questions/create_question.html', {'part': part})

    def post(self, request, part):
        if part == 'part1':
            form = Part1QuestionForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data['question_txt']
                category = form.cleaned_data['question_category']
                question = Part1Question.objects.create(question_txt=text, question_category=category)

                audio_file_path = generate_audio(question.id, text, 1)
                question.voice_url = audio_file_path
                question.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors})

        elif part == 'part2':
            form = Part2QuestionForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data['question_txt']
                question = Part2Question.objects.create(question_txt=text)

                audio_file_path = generate_audio(question.id, text, 2)
                question.voice_url = audio_file_path
                question.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors})

        elif part == 'part3':
            form = Part3QuestionForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data['question_txt']
                part2_id = request.POST.get('part2_question')
                part2 = Part2Question.objects.get(id=part2_id)
                question = Part3Question.objects.create(question_txt=text, part2_question=part2)

                audio_file_path = generate_audio(question.id, text, 3)
                question.voice_url = audio_file_path
                question.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors})


# @csrf_exempt
class GenerateAudioView(CreateAPIView):
    serializer_class = QuestionTTSInputSerializer
    authentication_classes = []

    @swagger_auto_schema(request_body=QuestionTTSInputSerializer,
                         operation_description="Generate audio file from text, this audio is temporary and will be removed",)
    def post(self, request):
        serializer = QuestionTTSInputSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            text = data.get('text')
            part_number = data.get('part_number', 1)
            id_ = data.get('id_', 0)
            lang = data.get('lang')
            gender = data.get('gender').lower()

            host_name = request.get_host()
            is_local = host_name.startswith('localhost')
            if is_local:
                url = f'http://{host_name}'
            else:
                url = f'https://{host_name}'

            audio_file_path = generate_audio(id_, text, part_number, lang, gender)
            audio_file_path = url + audio_file_path

            return JsonResponse({'audio_url': audio_file_path})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
