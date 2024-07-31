from rest_framework.parsers import MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from school_api.models import SchoolPart2Result
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from school_api.tasks import process_part2_result_task
from rest_framework.authentication import BasicAuthentication
from school_api.serializers import SchoolPart2ResultCreateSerializer, DefaultResponseSerializer


class SchoolPart2ResultCreateView(generics.CreateAPIView):
    serializer_class = SchoolPart2ResultCreateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    parser_classes = [MultiPartParser, ]
    @swagger_auto_schema(
        operation_description="Create a new part 2 result",
        responses={
            200: DefaultResponseSerializer,
            400: "Bad Request",
        }, request_body=SchoolPart2ResultCreateSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            question = serializer.validated_data.get('question')
            session = serializer.validated_data.get('session')
            voice_audio_file = serializer.validated_data.get('voice_audio')
            db_session: SchoolPart2Result = SchoolPart2Result.objects.get(session=session.id, question=question.id)
            db_session.voice_audio = voice_audio_file
            db_session.tts_name = 'whisper'
            db_session.status = 'pending'
            db_session.save()
            process_part2_result_task.delay(
                result_id_pk=db_session.id)
            return Response(DefaultResponseSerializer(
                {'msg': 'ok'},).data,
                status=status.HTTP_201_CREATED
            )