from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from community.models import Question


class QuestionCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="secret")
        self.url = reverse("question_create")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_question_create_form_view_get(self):
        self.client.login(username="testuser", password="secret")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ask a New Question")

    def test_question_create_post_valid_data(self):
        self.client.login(username="testuser", password="secret")
        form_data = {
            "title": "How to write unit tests in Django?",
            "description": "I'm trying to test CBV in Django. Need help with examples.",
            "tags": "django,testing,cbv",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, reverse("question_list"))
        self.assertEqual(Question.objects.count(), 1)
        question = Question.objects.first()
        self.assertEqual(question.title, form_data["title"])
        self.assertEqual(question.author, self.user)
