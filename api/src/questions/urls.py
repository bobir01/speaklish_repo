# urls.py
from django.urls import path
from . import views
from .views import Part1QuestionListAPIView, Part2QuestionListAPIView, Part3QuestionListAPIView
from .views import Part1QuestionCreateAPIView, Part2QuestionCreateAPIView, Part3QuestionCreateAPIView
from .views import Part1QuestionRetrieveUpdateDestroyAPIView, Part2QuestionRetrieveUpdateDestroyAPIView, \
    Part3QuestionRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('part1/', Part1QuestionListAPIView.as_view(), name='part1_question_list'),
    path('part1/create/', Part1QuestionCreateAPIView.as_view(), name='create_part1_question'),
    path('part1/<int:pk>/', Part1QuestionRetrieveUpdateDestroyAPIView.as_view(), name='part1_question_detail'),

    path('part2/', Part2QuestionListAPIView.as_view(), name='part2_question_list'),
    path('part2/create/', Part2QuestionCreateAPIView.as_view(), name='create_part2_question'),
    path('part2/<int:pk>/', Part2QuestionRetrieveUpdateDestroyAPIView.as_view(), name='part2_question_detail'),

    path('part3/', Part3QuestionListAPIView.as_view(), name='part3_question_list'),
    path('part3/create/', Part3QuestionCreateAPIView.as_view(), name='create_part3_question'),
    path('part3/<int:pk>/', Part3QuestionRetrieveUpdateDestroyAPIView.as_view(), name='part3_question_detail'),

    path('create/<str:part>/', views.CreateQuestionView.as_view(), name='create_question'),
    path('generate_audio/', views.GenerateAudioView.as_view(), name='generate_audio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

]
