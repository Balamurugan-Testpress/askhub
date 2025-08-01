from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from community.models import Question


class EditDeleteViewsTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pass123")
        self.other_user = User.objects.create_user(username="other", password="pass123")

        self.question = Question.objects.create(
            title="Sample Question",
            description="Sample description",
            author=self.author,
        )

    def login(self, user="author"):
        self.client.login(username=user, password="pass123")

    def test_question_edit_view_authorized(self):
        self.login()

        self.question.author = self.author
        self.question.save()

        url = reverse("question_edit", args=[self.question.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/question/edit.html")

        updated_data = {
            "title": "Updated question title",
            "description": "Updated question content",
            "tags": "new,old",
        }
        response = self.client.post(url, updated_data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.question.refresh_from_db()
        self.assertEqual(self.question.title, "Updated question title")
        self.assertEqual(self.question.description, "Updated question content")

    def test_question_edit_view_unauthorized(self):
        self.login("other")
        url = reverse("question_edit", args=[self.question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_delete_view_authorized(self):
        self.login()
        url = reverse("question_delete", args=[self.question.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/question/confirm_delete.html")

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
