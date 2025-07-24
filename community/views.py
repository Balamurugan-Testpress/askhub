from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import FormMixin
from taggit.models import Tag

from community.forms import AnswerForm, QuestionForm
from .filters import QuestionFilter
from .models import Answer, Comment, Question


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
    context_object_name = "question"

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


class AnswerDetailView(LoginRequiredMixin, FormMixin, DetailView):
    template_name = "community/answer/detail.html"
    model = Answer
    form_class = CommentForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            Answer,
            pk=self.kwargs["answer_id"],
            question_id=self.kwargs["question_id"],
        )

    def get_success_url(self):
        return reverse(
            "answer_detail",
            kwargs={
                "question_id": self.object.question_id,
                "answer_id": self.object.pk,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = (
            self.object.comments.select_related("author")
            .prefetch_related("votes")
            .order_by("-created_at")
        )
        context["comment_form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.answer = self.object
            comment.author = request.user

            parent_comment_id = request.POST.get("parent_comment_id")
            if parent_comment_id:
                try:
                    parent = Comment.objects.get(id=parent_comment_id)
                    comment.parent_comment = parent
                    comment.answer = None
                except Comment.DoesNotExist:
                    pass

            comment.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


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
        form.instance.question = self.question
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["question"] = self.question
        return context

    def get_success_url(self):
        return reverse("question_detail", kwargs={"question_id": self.question.pk})
