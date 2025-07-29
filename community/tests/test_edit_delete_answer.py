from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from community.models import Question, Answer


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

    def login(self, user="author"):
        self.client.login(username=user, password="pass123")

    def test_answer_delete_view_authorized(self):
        self.login()
        url = reverse("answer_delete", args=[self.question.id, self.answer.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/answer/confirm_delete.html")

        response = self.client.post(url)
        self.assertRedirects(
            response, reverse("question_detail", args=[self.question.id])
        )
        self.assertFalse(Answer.objects.filter(id=self.answer.id).exists())

    def test_answer_edit_view_unauthorized(self):
        self.login("other")
        url = reverse("answer_edit", args=[self.question.id, self.answer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_login_required_for_edit_and_delete(self):
        urls = [
            reverse("answer_edit", args=[self.question.id, self.answer.id]),
            reverse("answer_delete", args=[self.question.id, self.answer.id]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_answer_edit_view_authorized(self):
        self.login()
        url = reverse("answer_edit", args=[self.question.id, self.answer.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/answer/edit.html")

        updated_data = {
            "content": "Updated answer content",
        }
        response = self.client.post(url, updated_data)

        self.assertRedirects(
            response, reverse("answer_detail", args=[self.answer.id, self.question.id])
        )

        self.answer.refresh_from_db()
        self.assertEqual(self.answer.content, "Updated answer content")
