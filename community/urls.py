from django.urls import path
from community.views import QuestionListView

urlpatterns = [
    path("", QuestionListView.as_view(), name="question_list"),
]
