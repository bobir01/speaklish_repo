from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.models import Part2Question, UserPart2Result
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView

from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from api.serializers import UserPart2ResultCreateSerializer, Part2QuestionSerializer
from api.tasks import process_part2_result_task


class UserPart2ResultCreateAPIView(CreateAPIView):
    serializer_class = UserPart2ResultCreateSerializer
    parser_classes = [MultiPartParser, ]
    @swagger_auto_schema(
        auto_schema=None,
        operation_description="Create a new part-2 result",
        responses={
            200: UserPart2ResultCreateSerializer,
            400: "Bad Request",
            404: "Not Found",
        },

        tags=['user-result'],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        part2: UserPart2Result = serializer.save()
        process_part2_result_task.delay(part2.id)

        return Response({"msg": "ok",
                         "id": part2.id,
                         }, status=200)


class Part2QuestionAPIView(ListAPIView):
    serializer_class = Part2QuestionSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Part2Question.objects.all()

    @swagger_auto_schema(
        operation_description="Get all part-1 questions",
        responses={
            200: Part2QuestionSerializer(many=True),
            400: "Bad Request",
        },
        tags=['question-set'],
    )
    def get(self, request, *args, **kwargs):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)
