from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from community.models import Question


class QuestionListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        for i in range(15):
            q = Question.objects.create(
                author=self.user,
                title=f"Test Question {i + 1}",
                description="Sample description",
            )
            q.tags.add(f"tag_{i + 1}")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("question_list"))
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_logged_in_user_can_see_paginated_questions(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("question_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/question_list.html")
        self.assertTrue("question_list" in response.context)
        self.assertEqual(len(response.context["question_list"]), 10)

    def test_second_page_has_remaining_questions(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("question_list") + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["question_list"]), 5)

    def test_filter_using_tags(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("question_list") + "?q=&tag=tag_1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["question_list"]), 1)
