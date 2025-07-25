from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from community.models import Question, Answer, Vote


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

    def test_toggle_vote(self):
        url = self.vote_url("question", self.question.id, 1)

        self.client.post(url)
        self.assertEqual(Vote.objects.count(), 1)

        self.client.post(url)
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
