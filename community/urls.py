from django.urls import path
from community.views import AnswerDetailView, QuestionDetailView, QuestionListView

urlpatterns = [
    path("", QuestionListView.as_view(), name="question_list"),
    path(
        "question/<int:question_id>/",
        QuestionDetailView.as_view(),
        name="question_detail",
    ),
    path(
        "question/<int:question_id>/answer/<int:answer_id>/",
        AnswerDetailView.as_view(),
        name="answer_detail",
    ),
]
