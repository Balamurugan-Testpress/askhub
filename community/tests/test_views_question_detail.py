from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from community.models import Question


class QuestionDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.question = Question.objects.create(
            author=self.user,
            title="Test Question",
            description="Sample description",
        )
        self.question.tags.add("tag_1")

    def test_redirect_if_not_logged_in(self):
        url = reverse("question_detail", args=[self.question.pk])
        response = self.client.get(url)
        self.assertRedirects(
            response, f"/accounts/login/?next=/question/{self.question.pk}/"
        )

    def test_logged_in_user_can_see_question_detail(self):
        self.client.login(username="testuser", password="pass123")
        url = reverse("question_detail", args=[self.question.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/question/detail.html")
        self.assertEqual(response.context["object"], self.question)

    def test_question_not_found(self):
        self.client.login(username="testuser", password="pass123")
        url = reverse("question_detail", args=[999])  # No question with pk=999 exists
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
