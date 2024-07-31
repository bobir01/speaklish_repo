from django.urls import path
from writing_checker.views import Task1EssayCreateView, Task1EssayRetrieveView
from writing_checker.views import Task2EssayCreateView, Task2EssayRetrieveView

urlpatterns = [
    path("task1-create/", Task1EssayCreateView.as_view(), name="task1-create"),
    path('task1-get/<int:id>/', Task1EssayRetrieveView.as_view(), name='task1-get'),
    path("task2-create/", Task2EssayCreateView.as_view(), name="task2-create"),
    path('task2-get/<int:id>/', Task2EssayRetrieveView.as_view(), name='task2-get'),
]
