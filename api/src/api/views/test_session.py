from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from api.utils.logger import logged
# from

from api.models import TestSession, Part1Question, Part2Question, Part3Question
from api.serializers import TestSessionCreateSerializer, Part1QuestionSerializer, Part2QuestionSerializer, \
    Part3QuestionSerializer


class TestSessionCreateAPIView(CreateAPIView):
    serializer_class = TestSessionCreateSerializer

    @swagger_auto_schema(
        auto_schema=None,
        operation_description="Create a new test session, in response you will get a session id and questions",
        responses={
            200: "Success",
            400: "Bad Request",
            404: "Not Found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Id of the user"),

            },
            required=['user']
        ),
        tags=['test-session-user'],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        session: TestSession = serializer.save()
        log_msg = "session %s created" % session.id
        logged(log_msg)
        part1_questions = Part1Question.objects.filter(question_category_id=Part1Question.get_random_question(),
                                                       is_active=True).all()
        part2_question = Part2Question.get_random_question().first()
        part3_questions = Part3Question.objects.filter(part2_question_id=part2_question,
                                                       is_active=True).all()

        response = {
            "msg": "ok",
            "id": session.id,
            "part1_questions": Part1QuestionSerializer(part1_questions, many=True).data,
            "part2_question": Part2QuestionSerializer(part2_question).data,
            "part3_questions": Part3QuestionSerializer(part3_questions, many=True).data,
        }
        return Response(response, status=200)

    @swagger_auto_schema(
        auto_schema=None,
        operation_description="Get the result of the session",
        responses={
            200: "Success",
            400: "Bad Request",
            404: "Not Found",
        },
        manual_parameters=[
            openapi.Parameter(
                name='session_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='Id of the session',
            ),

        ],
        tags=['test-session'],
    )
    def get(self, request):
        """which requires a session id and returns the result of the session
        """
        qs = self.request.query_params

        logged(qs)
        if qs.get('session_id') is None:

            return Response({"msg": "session id is required"}, status=400)
        session_result = TestSession.objects.filter(id=int(qs.get('session_id')[0]))

        if not session_result.exists():
            return Response({"msg": "session %s not found" % qs.get('session_id')
                             }, status=404)

        session_result = session_result.first()

        if session_result.result is None:
            return Response({"msg": "waiting"}, status=202)

        return Response({"msg": "ok",
                         "id": session_result.id,
                         "result": session_result.result,
                         }, status=200)
