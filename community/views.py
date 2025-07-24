from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from taggit.models import Tag

from community.forms import AnswerForm, QuestionForm

from .filters import QuestionFilter
from .models import Answer, Question


class QuestionListView(LoginRequiredMixin, ListView):
    model = Question
    template_name = "community/question/list.html"
    ordering = "-created_at"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = QuestionFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_tags"] = Tag.objects.all()
        context["filterset"] = self.filterset
        return context


class QuestionDetailView(LoginRequiredMixin, DetailView):
    model = Question
    template_name = "community/question/detail.html"

    def get_object(self):
        question_id = self.kwargs["question_id"]
        return get_object_or_404(Question, pk=question_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_answers = (
            self.object.answers.select_related("author")
            .prefetch_related("votes")
            .order_by("-created_at")
        )

        page = self.request.GET.get("page")
        paginator = Paginator(all_answers, 5)

        try:
            answers = paginator.page(page)
        except PageNotAnInteger:
            answers = paginator.page(1)
        except EmptyPage:
            answers = paginator.page(paginator.num_pages)

        context["answers"] = answers
        return context


class AnswerDetailView(LoginRequiredMixin, DetailView):
    template_name = "community/answer/detail.html"
    model = Answer
    context_object_name = "answer"

    def get_object(self):
        question_id = self.kwargs["question_id"]
        answer_id = self.kwargs["answer_id"]
        return get_object_or_404(Answer, pk=answer_id, question__id=question_id)


class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = "community/question/create.html"
    success_url = reverse_lazy("question_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class SubmitAnswerView(LoginRequiredMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = "community/answer/create.html"

    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=self.kwargs["question_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.question = self.question  # use already-fetched question
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["question"] = self.question
        return context

    def get_success_url(self):
        return reverse("question_detail", kwargs={"pk": self.question.pk})
