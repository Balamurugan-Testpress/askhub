from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from community.models import Question, Answer

User = get_user_model()


class SubmitAnswerViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="secret123")
        self.question = Question.objects.create(
            title="Why is testing important?",
            description="Explain the purpose and benefits of writing tests.",
            author=self.user,
        )
        self.url = reverse("submit_answer", kwargs={"question_id": self.question.pk})

    def test_login_required_for_get(self):
        """GET request should redirect to login if user is not authenticated"""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_login_required_for_post(self):
        """POST request should redirect to login if user is not authenticated"""
        response = self.client.post(self.url, {"content": "Testing is crucial!"})
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")
        self.assertEqual(Answer.objects.count(), 0)

    def test_render_form_authenticated(self):
        """GET request by authenticated user renders the form"""
        self.client.login(username="tester", password="secret123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/answer/create.html")
        self.assertContains(response, self.question.title)

    def test_submit_valid_answer(self):
        """POST valid answer should create a new Answer instance"""
        self.client.login(username="tester", password="secret123")
        response = self.client.post(
            self.url, {"content": "Testing helps prevent bugs."}
        )

        self.assertEqual(Answer.objects.count(), 1)
        answer = Answer.objects.first()
        self.assertEqual(answer.content, "Testing helps prevent bugs.")
        self.assertEqual(answer.author, self.user)
        self.assertEqual(answer.question, self.question)

        # Ensure redirection to question detail page
        expected_url = reverse(
            "question_detail", kwargs={"question_id": self.question.pk}
        )
        self.assertRedirects(response, expected_url)

    def test_submit_invalid_answer(self):
        """POST invalid answer (empty content) should show form with errors"""
        self.client.login(username="tester", password="secret123")
        response = self.client.post(self.url, {"content": ""})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "content", "This field is required.")
        self.assertEqual(Answer.objects.count(), 0)
