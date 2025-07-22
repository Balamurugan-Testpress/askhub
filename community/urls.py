from django.urls import path
<<<<<<< HEAD
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
=======
from community.views import AnswerDetailView, QuestionDetailView, QuestionListView

urlpatterns = [
    path("", QuestionListView.as_view(), name="question_list"),
    path("question/<int:pk>/", QuestionDetailView.as_view(), name="question_detail"),
    path(
        "question/<int:q_pk>/answer/<int:pk>/",
>>>>>>> e3fd15f (feat: implement question detail page and answer detail page)
        AnswerDetailView.as_view(),
        name="answer_detail",
    ),
]
