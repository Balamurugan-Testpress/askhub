from django import forms
from community.models import Answer, Question, Comment


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "description", "tags"]
        labels = {
            "title": "Question Title",
            "description": "Detailed Description",
            "tags": "Tags",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. How to use Django CBV with tags?",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Provide detailed explanation, code, or errors…",
                    "rows": 6,
                }
            ),
            "tags": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. django, python, forms",
                }
            ),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["content"]

        labels = {"content": "Answer Content"}
        help_texts = {"content": "State your answer here"}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
