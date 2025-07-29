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

    def test_comment_edit_view_authorized(self):
        self.login()
        url = reverse(
            "comment_edit",
            args=[self.question.id, self.answer.id, self.comment.id],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/comment/edit.html")

    def test_comment_edit_view_unauthorized(self):
        self.login("other")
        url = reverse(
            "comment_edit",
            args=[self.question.id, self.answer.id, self.comment.id],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_comment_delete_view_authorized(self):
        self.login()
        url = reverse(
            "comment_delete",
            args=[self.question.id, self.answer.id, self.comment.id],
        )
        response = self.client.post(url)
        self.assertRedirects(
            response,
            reverse("answer_detail", args=[self.question.id, self.answer.id]),
        )
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_comment_delete_view_unauthorized(self):
        self.login("other")
        url = reverse(
            "comment_delete",
            args=[self.question.id, self.answer.id, self.comment.id],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_login_required_for_edit_and_delete(self):
        urls = [
            reverse(
                "comment_edit", args=[self.question.id, self.answer.id, self.comment.id]
            ),
            reverse(
                "comment_delete",
                args=[self.question.id, self.answer.id, self.comment.id],
            ),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_comment_edit_post_success(self):
        self.login()
        url = reverse(
            "comment_edit",
            args=[self.question.id, self.answer.id, self.comment.id],
        )
        new_content = "Updated comment content"
        response = self.client.post(url, {"content": new_content})

        self.assertRedirects(
            response,
            reverse("answer_detail", args=[self.question.id, self.answer.id]),
        )

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, new_content)
