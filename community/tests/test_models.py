from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Question, Answer, Comment, Vote
from taggit.models import Tag


class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.question = Question.objects.create(
            author=self.user,
            title="What is Django?",
            description="Explain Django framework.",
        )
        self.question.tags.add("django")

        self.answer = Answer.objects.create(
            question=self.question,
            author=self.user,
            content="Django is a Python web framework.",
        )

        self.comment = Comment.objects.create(
            author=self.user, answer=self.answer, content="Thanks for the answer!"
        )

        self.reply = Comment.objects.create(
            author=self.user, parent_comment=self.comment, content="You're welcome!"
        )

    def test_question_creation(self):
        self.assertEqual(self.question.title, "What is Django?")
        self.assertEqual(self.question.author, self.user)
        self.assertEqual(self.question.answers.count(), 1)
        self.assertIn("django", [tag.name for tag in self.question.tags.all()])

    def test_answer_creation(self):
        self.assertEqual(self.answer.question, self.question)
        self.assertEqual(self.answer.author, self.user)
        self.assertEqual(self.answer.votes.count(), 0)

    def test_comment_on_answer(self):
        self.assertEqual(self.comment.answer, self.answer)
        self.assertEqual(self.comment.content, "Thanks for the answer!")

    def test_reply_to_comment(self):
        self.assertEqual(self.reply.parent_comment, self.comment)
        self.assertIn(self.reply, self.comment.replies.all())

    def test_vote_on_question(self):
        vote = Vote.objects.create(
            user=self.user, vote_type=1, content_object=self.question
        )
        self.assertEqual(self.question.votes.count(), 1)
        self.assertEqual(vote.content_object, self.question)

    def test_vote_on_answer(self):
        vote = Vote.objects.create(
            user=self.user, vote_type=-1, content_object=self.answer
        )
        self.assertEqual(self.answer.votes.count(), 1)
        self.assertEqual(vote.content_object, self.answer)

    def test_vote_on_comment(self):
        vote = Vote.objects.create(
            user=self.user, vote_type=1, content_object=self.comment
        )
        self.assertEqual(self.comment.votes.count(), 1)
        self.assertEqual(vote.content_object, self.comment)
