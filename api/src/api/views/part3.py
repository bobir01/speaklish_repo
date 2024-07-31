from api.models import Part3Question, UserPart3Result
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from api.serializers import UserPart3ResultCreateSerializer, Part3QuestionSerializer
from api.tasks import process_part3_result_task, process_feedback_task


class UserPart3ResultCreateAPIView(CreateAPIView):
    serializer_class = UserPart3ResultCreateSerializer
    parser_classes = [MultiPartParser, ]

    @swagger_auto_schema(
        auto_schema=None,
        operation_description="Create a new part-3 result",
        responses={
            200: UserPart3ResultCreateSerializer,
            400: "Bad Request",
            404: "Not Found",
        },

        tags=['user-result'],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        part3: UserPart3Result = serializer.save()
        process_part3_result_task.delay(part3.id)
        # number part3 questions
        part3_results_count = UserPart3Result.objects.filter(session_id=part3.session_id).count()
        part3_questions_count = Part3Question.objects.filter(part2_question_id=part3.question.part2_question).count()
        if part3_results_count == part3_questions_count:
            process_feedback_task.delay(part3.session_id)
            return Response({"msg": "ok, processing for final result",
                             "id": part3.id,
                             }, status=200)
        return Response({"msg": "ok",
                         "id": part3.id,
                         }, status=200)


class Part3QuestionAPIView(ListAPIView):
    serializer_class = Part3QuestionSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Part3Question.objects.all()

    @swagger_auto_schema(
        operation_description="Get all part-3 questions",
        responses={
            200: Part3QuestionSerializer(many=True),
            400: "Bad Request",
        },
        tags=['question-set'],
    )
    def get(self, request, *args, **kwargs):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=200)
