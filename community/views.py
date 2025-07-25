from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.fields import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View
from django.views.generic.edit import FormMixin
from taggit.models import Tag
from django.db.models import Sum
from community.forms import AnswerForm, CommentForm, QuestionForm

from .filters import QuestionFilter
from .models import Answer, Comment, Question, Vote


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
            .annotate(score=Sum("votes__vote_type"))
            .order_by("-score", "-created_at")
        )
        user = self.request.user
        context["user_vote_type"] = self.object.get_user_vote(user)
        vote_map = {answer.id: answer.get_user_vote(user) for answer in all_answers}
        context["answer_vote_map"] = vote_map

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
        user = self.request.user

        comments = (
            self.object.comments.select_related("author")
            .prefetch_related("votes")
            .order_by("-created_at")
        )
        context["comments"] = comments
        context["comment_form"] = self.get_form()
        context["user_vote_type"] = self.object.get_user_vote(user)

        if user.is_authenticated:
            comment_ids = comments.values_list("id", flat=True)
            vote_qs = Vote.objects.filter(
                user=user,
                content_type=ContentType.objects.get_for_model(Comment),
                object_id__in=comment_ids,
            ).values_list("object_id", "vote_type")
            context["comment_vote_map"] = {
                obj_id: vote_type for obj_id, vote_type in vote_qs
            }
        else:
            context["comment_vote_map"] = {}
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.answer = self.object
            comment.author = request.user

            parent = self.get_parent_comment(request)
            if parent:
                comment.parent_comment = parent

            comment.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_parent_comment(self, request):
        parent_comment_id = request.POST.get("parent_comment_id")
        if parent_comment_id:
            try:
                return Comment.objects.get(id=parent_comment_id)
            except Comment.DoesNotExist:
                return None
        return None


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
        return reverse("question_detail", kwargs={"question_id": self.question.pk})


class VoteView(LoginRequiredMixin, View):
    def post(self, request, model_name, object_id, vote_type):
        try:
            vote_type = int(vote_type)
            if vote_type not in [1, -1]:
                return HttpResponseBadRequest("Invalid vote type.")
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid vote type.")

        model_map = {
            "question": Question,
            "answer": Answer,
            "comment": Comment,
        }

        model = model_map.get(model_name)
        if not model:
            return HttpResponseBadRequest("Invalid model.")

        obj = get_object_or_404(model, pk=object_id)
        content_type = ContentType.objects.get_for_model(model)
        user_vote_type = 0
        vote, created = Vote.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            defaults={"vote_type": vote_type},
        )

        if not created:
            if vote.vote_type == vote_type:
                vote.delete()
                user_vote_type = 0
            else:
                vote.vote_type = vote_type
                vote.save()
                user_vote_type = vote_type
        else:
            user_vote_type = vote_type

        return render(
            request,
            "community/partials/vote_buttons.html",
            {
                "obj": obj,
                "model_name": model_name,
                "user_vote_type": user_vote_type,
            },
        )
