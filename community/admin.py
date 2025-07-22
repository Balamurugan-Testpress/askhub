from django.contrib import admin
from .models import Question, Answer, Comment


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title", "description")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "author", "created_at")
    search_fields = ("content",)
    list_filter = ("created_at", "author")
    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "created_at", "answer", "parent_comment")
    search_fields = ("content",)
    list_filter = ("created_at", "author")
    ordering = ("-created_at",)
