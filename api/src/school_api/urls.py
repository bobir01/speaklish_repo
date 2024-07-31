from django.urls import path

from school_api.views.part1 import SchoolPart1ResultCreateView
from school_api.views.part2 import SchoolPart2ResultCreateView
from school_api.views.part3 import SchoolPart3ResultCreateView
from school_api.views.send_message import send_message

from school_api.views.test_session import SchoolTestSessionCreateAPIView, SchoolTestSessionResultAPIView

urlpatterns = [
    path("session-create/", SchoolTestSessionCreateAPIView.as_view(), name="school-session-create"),
    path("session-feedback/<int:pk>", SchoolTestSessionResultAPIView.as_view(), name="school-session-feedback"),
    path("part-1-create/", SchoolPart1ResultCreateView.as_view(), name="school-part-1-create"),
    path("part-2-create/", SchoolPart2ResultCreateView.as_view(), name="school-part-2-create"),
    path("part-3-create/", SchoolPart3ResultCreateView.as_view(), name="school-part-3-create"),
    path("send-message/", send_message, name="school-send-message"),

]
