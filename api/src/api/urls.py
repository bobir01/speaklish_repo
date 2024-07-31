from django.urls import path

from api import views

urlpatterns = [
    path('test-session/', views.test_session.TestSessionCreateAPIView.as_view(), name="test-session"),
    path("user-part-1-create/", views.part1.UserPart1ResultCreateAPIView.as_view(), name="user-part-1-create"),
    path("user-part-2-create/", views.part2.UserPart2ResultCreateAPIView.as_view(), name="user-part-2-create"),
    path("user-part-3-create/", views.part3.UserPart3ResultCreateAPIView.as_view(), name="user-part-3-create"),
    path("part-1-questions/", views.part1.Part1QuestionAPIView.as_view(), name="part-1-questions"),
    path("part-2-questions/", views.part2.Part2QuestionAPIView.as_view(), name="part-2-questions"),
    path("part-3-questions/", views.part3.Part3QuestionAPIView.as_view(), name="part-3-questions"),
]
