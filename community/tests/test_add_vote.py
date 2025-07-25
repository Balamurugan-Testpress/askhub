from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from community.models import Question, Answer, Comment, Vote


class VoteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="voter", password="testpass")
        self.client.login(username="voter", password="testpass")

        self.question = Question.objects.create(
            author=self.user, title="Sample Question", description="Some description"
        )
        self.answer = Answer.objects.create(
            question=self.question, author=self.user, content="Sample answer"
        )
        self.comment = Comment.objects.create(
            author=self.user, content="A comment", answer=self.answer
        )

    def vote_url(self, model_name, obj_id, vote_type):
        return reverse("vote", args=[model_name, obj_id, vote_type])

    def test_upvote_question(self):
        url = self.vote_url("question", self.question.id, 1)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        vote = Vote.objects.get()
        self.assertEqual(vote.vote_type, 1)
        self.assertEqual(vote.content_object, self.question)

    def test_downvote_question(self):
        url = self.vote_url("question", self.question.id, -1)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        vote = Vote.objects.get()
        self.assertEqual(vote.vote_type, -1)
        self.assertEqual(vote.content_object, self.question)

    def test_toggle_vote_removes_existing_vote(self):
        url = self.vote_url("question", self.question.id, 1)
        self.client.post(url)
        self.assertEqual(Vote.objects.count(), 1)

        self.client.post(url)  # toggling same vote
        self.assertEqual(Vote.objects.count(), 0)

    def test_change_vote_type(self):
        upvote_url = self.vote_url("question", self.question.id, 1)
        downvote_url = self.vote_url("question", self.question.id, -1)

        self.client.post(upvote_url)
        vote = Vote.objects.get()
        self.assertEqual(vote.vote_type, 1)

        self.client.post(downvote_url)
        vote.refresh_from_db()
        self.assertEqual(vote.vote_type, -1)

    def test_answer_voting(self):
        url = self.vote_url("answer", self.answer.id, 1)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        vote = Vote.objects.get()
        self.assertEqual(vote.content_object, self.answer)
        self.assertEqual(vote.vote_type, 1)

    def test_comment_voting(self):
        url = self.vote_url("comment", self.comment.id, 1)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        vote = Vote.objects.get()
        self.assertEqual(vote.content_object, self.comment)
        self.assertEqual(vote.vote_type, 1)

    def test_votes_are_user_specific(self):
        other_user = User.objects.create_user(username="other", password="pass")
        Vote.objects.create(
            user=other_user,
            vote_type=1,
            content_type=ContentType.objects.get_for_model(self.question),
            object_id=self.question.id,
        )

        self.client.post(self.vote_url("question", self.question.id, -1))
        self.assertEqual(Vote.objects.count(), 2)

        my_vote = Vote.objects.get(user=self.user)
        self.assertEqual(my_vote.vote_type, -1)

    def test_invalid_model_name_returns_400(self):
        response = self.client.post(self.vote_url("invalid", self.question.id, 1))
        self.assertEqual(response.status_code, 400)

    def test_invalid_object_id_returns_404(self):
        response = self.client.post(self.vote_url("question", 9999, 1))
        self.assertEqual(response.status_code, 404)

    def test_invalid_vote_type_ignored_or_400(self):
        # depending on your view, this may be 400 or ignored
        response = self.client.post(self.vote_url("question", self.question.id, 2))
        self.assertIn(response.status_code, [400, 200])
        # Ensure no vote is recorded
        self.assertEqual(Vote.objects.count(), 0)

    def test_vote_requires_login(self):
        self.client.logout()
        url = self.vote_url("question", self.question.id, 1)
        response = self.client.post(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(Vote.objects.count(), 0)

    def test_duplicate_vote_different_objects(self):
        q_vote_url = self.vote_url("question", self.question.id, 1)
        a_vote_url = self.vote_url("answer", self.answer.id, 1)

        self.client.post(q_vote_url)
        self.client.post(a_vote_url)

        self.assertEqual(Vote.objects.count(), 2)
        self.assertTrue(Vote.objects.filter(content_type__model="question").exists())
        self.assertTrue(Vote.objects.filter(content_type__model="answer").exists())
