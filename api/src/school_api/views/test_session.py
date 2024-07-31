from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction as transaction
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.shortcuts import get_object_or_404
from api.serializers import Part1QuestionSerializer, Part2QuestionSerializer, Part3QuestionSerializer
from api.utils.logger import logged
from api.models import Part1Question, Part2Question, Part3Question
from school_api.models import TestSessionSchool, SchoolPart1Result, SchoolPart2Result, SchoolPart3Result, SchoolProfile, \
    SchoolReferralQuestionSet
from school_api.serializers import SchoolTestSessionCreateSerializer, SchoolTestSessionResultSerializer


class SchoolTestSessionCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    serializer_class = SchoolTestSessionCreateSerializer

    def query_params(self):
        return self.request.query_params

    @swagger_auto_schema(
        operation_description="Create a new test session, in response you will get a session_id and questions",
        responses={
            200: SchoolTestSessionCreateSerializer,
            400: "Bad Request",
            404: "Not Found",
        },
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description="Id of the user", required=True),
            openapi.Parameter('is_test', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description="Is this a test session"),
            openapi.Parameter('referral_code', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Referral code if any")]
    )
    def get(self, request):
        user = request.user
        qs = SchoolProfile.objects.select_related('school').filter(school=user)
        school_profile: SchoolProfile = get_object_or_404(qs)
        referral_code = self.query_params().get('referral_code')
        referral_school_qs = SchoolReferralQuestionSet.objects.filter(referral_name=referral_code)
        if not referral_school_qs.exists() and referral_code is not None:
            return Response({"msg": "Referral code `%s` not found" % referral_code}, status=404)
        if not school_profile.school.is_active:
            return Response(
                {"msg": "Account associated with School %s is not active, contact admins" % school_profile.school_name
                 }, status=400)
        if school_profile.session_count > 0:
            @transaction.atomic
            def update_session_count():
                school_profile.session_count -= 1
                school_profile.save()
                return school_profile

            school_profile = update_session_count()
        else:
            return Response({"msg": "No more sessions left for School %s" % school_profile.school_name
                             }, status=400)
        is_test = self.query_params().get('is_test') == 'true'
        user_id = self.query_params().get('user_id')
        session: TestSessionSchool = TestSessionSchool.objects.create(school=request.user,
                                                                      is_test=is_test,
                                                                      student_id=user_id)
        session.refresh_from_db()
        log_msg = "session %s created with user_id: %s " % (session.id, user_id)
        random_question = Part1Question.get_random_question(is_test=is_test)

        logged(log_msg)
        if referral_code is not None:
            referral_school: SchoolReferralQuestionSet = referral_school_qs.first()
            part1_questions = Part1Question.objects.select_related('question_category').filter(
                question_category=referral_school.part1_category.first(), is_active=True).order_by('id').all()
            part2_question = referral_school.part2_questions.first()
            part3_questions = Part3Question.objects.filter(part2_question_id=part2_question, is_active=True).order_by(
                'id').all()
        else:
            part1_questions = Part1Question.objects.select_related('question_category').filter(
                question_category=random_question).order_by('id').all()
            part2_question = Part2Question.get_random_question(is_test=is_test)
            part3_questions = Part3Question.objects.filter(part2_question_id=part2_question, is_active=True
                                                           ).order_by('id').all()

        SchoolPart1Result.objects.bulk_create(
            [SchoolPart1Result(school=user,
                               question=question,
                               session=session) for question in part1_questions])
        SchoolPart2Result.objects.create(school=user,
                                         question=part2_question,
                                         session=session)
        SchoolPart3Result.objects.bulk_create(
            [SchoolPart3Result(school=user,
                               question=question,
                               session=session) for question in part3_questions])
        session.refresh_from_db()
        response = {
            'user_id': session.student_id,
            'session_id': session.id,
            'referral_code': referral_code,
            "part1_questions": Part1QuestionSerializer(part1_questions, many=True).data,
            "part2_question": Part2QuestionSerializer(part2_question, ).data,
            "part3_questions": Part3QuestionSerializer(part3_questions, many=True).data,
        }
        return Response(response, status=200)


class SchoolTestSessionResultAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    serializer_class = SchoolTestSessionResultSerializer
    queryset = TestSessionSchool.objects.all()
    lookup_field = 'pk'

    @swagger_auto_schema(
        operation_description="Get the result of the session",
        responses={
            200: SchoolTestSessionResultSerializer,
            202: "Accepted",
            400: "Bad Request",
            404: "Not Found",
        })
    def get(self, request, pk):
        session = self.get_object()
        logged("pk %d, session %s result requested" % (pk, session.id))
        if session.result is None:
            return Response({"msg": "waiting"}, status=202)
        elif session.result is not None:
            data = SchoolTestSessionResultSerializer(session).data

            return Response(data, status=200)
        else:
            return Response({"msg": "session %s not found" % session.id
                             }, status=404)
