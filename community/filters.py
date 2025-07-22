from django.db.models import Q
from django_filters import FilterSet, CharFilter, ModelChoiceFilter
from taggit.models import Tag
from .models import Question


class QuestionFilter(FilterSet):
    q = CharFilter(method="filter_search")
    tag = ModelChoiceFilter(
        field_name="tags__name",
        to_field_name="name",
        queryset=Tag.objects.all(),
        method="filter_single_tag",
    )

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )

    def filter_single_tag(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(tags__name__iexact=value.name)

    class Meta:
        model = Question
        fields = []
