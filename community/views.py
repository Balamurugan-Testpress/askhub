from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from community.models import Question


@login_required
def home(request):
    return HttpResponse(f"Welcome home {request.user}")


class QuestionList(LoginRequiredMixin, ListView):
    model = Question
    template_name = "community/question_list.html"
    # context_object_name = "question_list"
    paginate_by = 10

    class Meta:
        ordering = ("-created_at",)
