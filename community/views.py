from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from .models import Question
from taggit.models import Tag


class QuestionListView(LoginRequiredMixin, ListView):
    model = Question
    template_name = "community/question_list.html"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q")
        tag_param = self.request.GET.get("tag", "").strip()
        queryset = Question.objects.all()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if tag_param:
            tag_list = [tag.strip() for tag in tag_param.split(",") if tag.strip()]
            for tag in tag_list:
                queryset = queryset.filter(tags__name__iexact=tag)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_tags"] = Tag.objects.all()

        tag_param = self.request.GET.get("tag", "")
        selected_tags = [tag.strip() for tag in tag_param.split(",") if tag.strip()]
        context["selected_tags"] = selected_tags

        context["search_query"] = self.request.GET.get("q", "")
        return context
