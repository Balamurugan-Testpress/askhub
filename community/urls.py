from django.urls import path
from community.views import (
    AnswerDetailView,
    QuestionCreateView,
    QuestionDetailView,
    QuestionListView,
    SubmitAnswerView,
)

urlpatterns = [
    path("", QuestionListView.as_view(), name="question_list"),
    path(
        "question/<int:question_id>/",
        QuestionDetailView.as_view(),
        name="question_detail",
    ),
    path("question/create/", QuestionCreateView.as_view(), name="question_create"),
    path(
        "question/<int:question_id>/answer/",
        SubmitAnswerView.as_view(),
        name="submit_answer",
    ),
    path(
        "question/<int:question_id>/answer/<int:answer_id>/",
        AnswerDetailView.as_view(),
        name="answer_detail",
    ),
]
