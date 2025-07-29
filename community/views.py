from collections import defaultdict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
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
    context_object_name = "question"

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
        context["answer_vote_map"] = self._get_answer_vote_map(
            self.request.user, all_answers
        )

        return context

    def _get_answer_vote_map(self, user, answers):
        if not user.is_authenticated:
            return {}

        answer_ids = [a.id for a in answers]
        vote_qs = Vote.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(Answer),
            object_id__in=answer_ids,
        ).values_list("object_id", "vote_type")

        return {obj_id: vote_type for obj_id, vote_type in vote_qs}


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

        all_comments = self._get_comments_with_author_and_votes()
        context["comments"] = self._build_comments_tree(all_comments)
        context["comment_form"] = self.get_form()
        context["user_vote_type"] = self.object.get_user_vote(user)
        context["comment_vote_map"] = self._get_comment_vote_map(user, all_comments)

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
        return self.form_invalid(form)

    def _create_comment_from_form(self, form, request):
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
                form.add_error(None, "The comment you are replying to does not exist.")
                return self.form_invalid(form)

        return comment

    def get_parent_comment(self, request):
        parent_comment_id = request.POST.get("parent_comment_id")
        if parent_comment_id:
            try:
                return Comment.objects.get(id=parent_comment_id)
            except Comment.DoesNotExist:
                return None
        return None

    def _get_comments_with_author_and_votes(self):
        return list(
            Comment.objects.filter(answer=self.object)
            .select_related("author")
            .prefetch_related("votes")
<<<<<<< HEAD
            .annotate(score=Sum("votes__vote_type"))
            .order_by("-score", "-created_at")
=======
>>>>>>> fdfa352 (feat: implement vote for comments,questions and answers)
        )

    def _get_comment_vote_map(self, user, comments):
        if not user.is_authenticated:
            return {}

        comment_ids = [c.id for c in comments]
        vote_qs = Vote.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(Comment),
            object_id__in=comment_ids,
        ).values_list("object_id", "vote_type")
        return {obj_id: vote_type for obj_id, vote_type in vote_qs}

    def _build_comments_tree(self, comments):
        children_map = defaultdict(list)
        for comment in comments:
            if comment.parent_comment_id:
                children_map[comment.parent_comment_id].append(comment)

        for comment in comments:
            comment.children = children_map.get(comment.id, [])

        return [c for c in comments if c.parent_comment_id is None]


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


class ToggleVoteView(LoginRequiredMixin, View):
    model_map = {
        "question": Question,
        "answer": Answer,
        "comment": Comment,
    }

    def post(self, request, model_name, object_id, vote_type):
        try:
            vote_type = int(vote_type)
            if vote_type not in [1, -1]:
                return HttpResponseBadRequest("Invalid vote type.")
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid vote type.")

        model = self.model_map.get(model_name)
        if not model:
            return HttpResponseBadRequest("Invalid model type.")

        obj = get_object_or_404(model, pk=object_id)
        user_vote_type = self._toggle_update_vote(
            request.user, model, object_id, vote_type
        )

        return render(
            request,
            "community/partials/vote_buttons.html",
            {
                "obj": obj,
                "model_name": model_name,
                "user_vote_type": user_vote_type,
            },
        )

    def _toggle_update_vote(self, user, model, object_id, vote_type):
        content_type = ContentType.objects.get_for_model(model)

        vote, created = Vote.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            defaults={"vote_type": vote_type},
        )

        if not created:
            if vote.vote_type == vote_type:
                vote.delete()
                return 0
            vote.vote_type = vote_type
            vote.save()

        return vote_type
