from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from community.models import Question, Answer, Comment


class EditDeleteViewsTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pass123")
        self.other_user = User.objects.create_user(username="other", password="pass123")

        self.question = Question.objects.create(
            title="Sample Question",
            description="Sample description",
            author=self.author,
        )

        self.answer = Answer.objects.create(
            content="Sample answer",
            question=self.question,
            author=self.author,
        )

        self.comment = Comment.objects.create(
            content="Sample comment",
            answer=self.answer,
            author=self.author,
        )

    def login(self, user="author"):
        self.client.login(username=user, password="pass123")

    def test_question_edit_view_authorized(self):
        self.login()
        url = reverse("question_edit", args=[self.question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/question/edit.html")

    def test_question_edit_view_unauthorized(self):
        self.login("other")
        url = reverse("question_edit", args=[self.question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_delete_view_authorized(self):
        self.login()
        url = reverse("question_delete", args=[self.question.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("question_list"))
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())

    def test_question_delete_view_unauthorized(self):
        self.login("other")
        url = reverse("question_delete", args=[self.question.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_login_required_for_edit_and_delete(self):
        urls = [
            reverse("question_edit", args=[self.question.id]),
            reverse("question_delete", args=[self.question.id]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"/accounts/login/?next={url}")
