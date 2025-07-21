from django import forms
from django.forms import fields
from community.models import Answer, Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "description"]
        labels = {
            "title": "Question Title",
            "description": "Detailed Description",
        }
        help_texts = {
            "title": "Describe your question concisely.",
            "description": "Add details, code samples, or context. Markdown supported.",
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["content"]

        labels = {"content": "Answer Content"}
        help_texts = {"content": "State your answer here"}


class Comment(forms.ModelForm):
    class Meta:
        model = Comment
