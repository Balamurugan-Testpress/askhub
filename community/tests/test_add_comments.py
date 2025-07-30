from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from community.models import Answer, Question, Comment  # Include Comment model


class AddCommentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test@123")
        self.question = Question.objects.create(
            title="Why is testing important?",
            description="Explain the purpose and benefits of writing tests.",
            author=self.user,
        )
        self.answer = Answer.objects.create(
            question=self.question,
            author=self.user,
            content="Tests make your code robust and prove nothing is broken.",
        )
        self.url = reverse(
            "answer_detail",
            kwargs={"question_id": self.question.pk, "answer_id": self.answer.pk},
        )

    def test_redirect_if_user_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_response_if_user_is_authenticated(self):
        self.client.login(username="testuser", password="test@123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/answer/detail.html")
        self.assertContains(response, self.answer.content)

    def test_submit_valid_comment(self):
        self.client.login(username="testuser", password="test@123")
        response = self.client.post(
            self.url, {"content": "This is a helpful answer!"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Comment.objects.filter(content="This is a helpful answer!").exists()
        )

    def test_invalid_comment_shows_errors(self):
        self.client.login(username="testuser", password="test@123")
        response = self.client.post(self.url, {"content": ""}, follow=True)
        self.assertContains(response, "This field is required.")

    def test_comment_saved_to_correct_answer(self):
        self.client.login(username="testuser", password="test@123")
        self.client.post(self.url, {"content": "Nice explanation."}, follow=True)
        comment = Comment.objects.get(content="Nice explanation.")
        self.assertEqual(comment.answer, self.answer)
        self.assertEqual(comment.author, self.user)

    def test_comment_count_increases(self):
        self.client.login(username="testuser", password="test@123")
        initial_count = Comment.objects.count()
        self.client.post(self.url, {"content": "Good point."}, follow=True)
        self.assertEqual(Comment.objects.count(), initial_count + 1)

    def test_anonymous_user_cannot_post_comment(self):
        response = self.client.post(
            self.url, {"content": "Anonymous shouldn't comment"}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertFalse(
            Comment.objects.filter(content="Anonymous shouldn't comment").exists()
        )

    def test_submit_valid_reply_to_comment(self):
        self.client.login(username="testuser", password="test@123")

        # First, create a parent comment
        parent_comment = Comment.objects.create(
            content="Parent comment",
            author=self.user,
            answer=self.answer,
        )

        # Now submit a reply to that comment
        response = self.client.post(
            self.url,
            {
                "content": "This is a reply",
                "parent_comment_id": str(parent_comment.pk),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        reply = Comment.objects.get(content="This is a reply")
        self.assertEqual(reply.parent_comment, parent_comment)
        self.assertEqual(reply.answer, self.answer)
        self.assertEqual(reply.author, self.user)

    def test_reply_with_invalid_parent_comment_id(self):
        self.client.login(username="testuser", password="test@123")

        response = self.client.post(
            self.url,
            {
                "content": "Trying invalid parent id",
                "parent_comment_id": "9999",
            },
            follow=True,
        )

        self.assertFalse(
            Comment.objects.filter(content="Trying invalid parent id").exists()
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, "form", None, "The comment you are replying to does not exist."
        )
