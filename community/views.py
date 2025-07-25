from urllib import request
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.fields import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View
from django.views.generic.edit import FormMixin
from taggit.models import Tag
from django.http import HttpResponse
from community.forms import AnswerForm, CommentForm, QuestionForm
from django.db.models import Sum
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_answers = (
            self.object.answers.select_related("author")
            .prefetch_related("votes")
            .order_by("-created_at")
        )
        question = self.get_object()
        user = self.request.user
        context["user_vote_type"] = question.get_user_vote(user)

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
        answer = self.get_object()
        user = self.request.user

        context["user_vote_type"] = answer.get_user_vote(user)

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
        self.question = get_object_or_404(Question, pk=self.kwargs["pk"])
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


class VoteView(LoginRequiredMixin, View):
    def post(self, request, model_name, object_id, vote_type):
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

        vote, created = Vote.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            defaults={"vote_type": vote_type},
        )

        if not created:
            print("not created")
            if vote.vote_type == int(vote_type):
                vote.delete()
                print("vote deleted")

            else:
                print("this works")
                vote.vote_type = vote_type
                vote.save()

                obj.refresh_from_db()
        user_vote = Vote.objects.filter(
            user=request.user, content_type=content_type, object_id=object_id
        ).first()
        return render(
            request,
            "community/partials/vote_buttons.html",
            {
                "obj": obj,
                "model_name": model_name,
                "user_vote_type": user_vote.vote_type if user_vote else 0,
            },
        )
