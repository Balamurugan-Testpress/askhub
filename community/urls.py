from django.urls import path
from community.views import AnswerDetailView, QuestionDetailView, QuestionListView

urlpatterns = [
    path("", QuestionListView.as_view(), name="question_list"),
    path("question/<int:pk>/", QuestionDetailView.as_view(), name="question_detail"),
    path(
        "question/<int:q_pk>/answer/<int:pk>/",
        AnswerDetailView.as_view(),
        name="answer_detail",
    ),
]
