from api.models import Part1Question, UserPart1Result
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import  IsAuthenticated

from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from api.serializers import UserPart1ResultCreateSerializer, Part1QuestionSerializer
from api.tasks import process_part1_result_task


class UserPart1ResultCreateAPIView(CreateAPIView):
    serializer_class = UserPart1ResultCreateSerializer
    parser_classes = [MultiPartParser, ]
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    @swagger_auto_schema(
        auto_schema=None,
        operation_description="Create a new part-1 result",
        responses={
            200: UserPart1ResultCreateSerializer,
            400: "Bad Request",
            404: "Not Found",
        },

        tags=['user-result'],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        part1: UserPart1Result = serializer.save()
        process_part1_result_task.delay(part1.id)

        return Response({"msg": "ok",
                         "id": part1.id,
                         }, status=200)


class Part1QuestionAPIView(ListAPIView):
    serializer_class = Part1QuestionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get_queryset(self):
        category_id = self.request.query_params.get('category_id')
        if category_id is not None:
            return Part1Question.objects.filter(question_category_id=category_id).all()
        return Part1Question.objects.all()

    @swagger_auto_schema(
        operation_description="""
Get all part-1 questions, it filters by category_id if it is 
provided in query params but if it is not provided it returns all questions
        """,
        responses={
            200: Part1QuestionSerializer(many=True),
            400: "Bad Request",
        },
        manual_parameters=[
            openapi.Parameter(
                name='category_id',
                in_=openapi.IN_QUERY,
                description='Id of the category',
                type=openapi.TYPE_INTEGER,
            ),
        ],
        tags=['question-set'],
    )
    def get(self, request, *args, **kwargs):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)
