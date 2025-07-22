from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from community.models import Question


class QuestionListView(LoginRequiredMixin, ListView):
    model = Question
    template_name = "community/question_list.html"
    paginate_by = 10

    def get_queryset(self):
        return Question.objects.order_by("-created_at")
