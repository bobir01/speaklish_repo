import json
import logging
import time

from writing_checker.models import Task1Essay, Task2Essay, WritingConfig
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from writing_checker.serializers import WritingTask1CreateSerializer, WritingTask1ResponseSerializer
from writing_checker.serializers import WritingTask2CreateSerializer, WritingTask2ResponseSerializer
from api.utils.ai_tools import check_writing_task1, check_writing_task2
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema


class Task1EssayCreateView(CreateAPIView):
    serializer_class = WritingTask1CreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, ]

    @swagger_auto_schema(
        operation_summary="Create Task1 Essay",
        operation_description="Create Task1 Essay",
        request_body=WritingTask1CreateSerializer,
        responses={201: WritingTask1ResponseSerializer,
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   503: "Service Unavailable"}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            config = WritingConfig.get_config()
            task1: Task1Essay = serializer.save()
            essay = task1.essay
            student_id = task1.student_id
            graph_url = task1.graph_image
            s_time = time.time()
            try:
                result, total_tokens, messages = check_writing_task1(essay, graph_url, config)
                logging.info(f"Task1 result: {result}")
                model_response = json.loads(result)
                task1.feedback = model_response.get(
                    'feedback', 'No feedback provided'
                )
            except json.JSONDecodeError as e:
                logging.error(f"Error in Task1: {e}")
                task1.feedback = 'Service unavailable, Please retry later, contact @Realm_AI to restore your sessions'
                return Response(task1.feedback, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            task1.token_usage = total_tokens
            task1.score = model_response.get('band_score', 0)
            messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": model_response
                    }
                ]
            })
            task1.prompt_json = messages
            task1.wait_time = time.time() - s_time
            task1.save()

            response = {
                'id': task1.id,
                'student_id': student_id,
                'feedback': task1.feedback,
                'score': {
                    'band_score': task1.score,
                    'task_response': model_response.get('task_response', 0),
                    'coherence_cohesion': model_response.get('coherence_cohesion', 0),
                    'lexical_resource': model_response.get('lexical_resource', 0),
                    'grammatical_accuracy': model_response.get('grammatical_accuracy', 0),
                },
                'token_usage': task1.token_usage,
                "word_count": task1.word_count
            }

            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Task1EssayRetrieveView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WritingTask1ResponseSerializer
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary="Retrieve Task1 Essay by id",
        operation_description="Retrieve Task1 Essay",

        responses={200: WritingTask1ResponseSerializer,
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   503: "Service Unavailable"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Task1Essay.objects.all()


class Task2EssayCreateView(CreateAPIView):
    serializer_class = WritingTask2CreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, ]

    @swagger_auto_schema(
        operation_summary="Create Task2 Essay",
        operation_description="Create Task2 Essay",
        request_body=WritingTask2CreateSerializer,
        responses={201: WritingTask1ResponseSerializer,
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   503: "Service Unavailable"}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            task2: Task2Essay = serializer.save()
            essay = task2.essay
            student_id = task2.student_id
            writing_config = WritingConfig.get_config()
            s_time = time.time()
            try:
                result, total_tokens, messages = check_writing_task2(essay, writing_config)
                logging.info(f"Task2 result: {result}")
                model_response = json.loads(result)
                task2.feedback = model_response.get(
                    'feedback', 'No feedback provided'
                )
            except json.JSONDecodeError as e:
                logging.error(f"Error in Task2: {e}")
                task2.feedback = 'Service unavailable, Please retry later, contact @Realm_AI to restore your sessions'
                return Response(task2.feedback, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            task2.token_usage = total_tokens
            task2.score = model_response.get('band_score', 0)
            messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": model_response
                    }
                ]
            })
            task2.prompt_json = messages
            task2.wait_time = time.time() - s_time
            task2.is_checked = True
            task2.model = writing_config.model_name
            task2.save()

            response = {
                'id': task2.id,
                'student_id': student_id,
                'feedback': task2.feedback,
                'score': {
                    'band_score': task2.score,
                    'task_response': model_response.get('task_response', 0),
                    'coherence_cohesion': model_response.get('coherence_cohesion', 0),
                    'lexical_resource': model_response.get('lexical_resource', 0),
                    'grammatical_accuracy': model_response.get('grammatical_accuracy', 0),
                },
                'token_usage': task2.token_usage,
            }

            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Task2EssayRetrieveView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WritingTask2ResponseSerializer
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary="Retrieve Task2 Essay by id",
        operation_description="Retrieve Task2 Essay",

        responses={200: WritingTask2ResponseSerializer,
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   503: "Service Unavailable"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Task2Essay.objects.all()
