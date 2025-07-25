from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from taggit.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.SmallIntegerField(choices=((1, "Upvote"), (-1, "Downvote")))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "user",
            "content_type",
            "object_id",
        )


class Votable(models.Model):
    votes = GenericRelation(Vote)

    class Meta:
        abstract = True

    @cached_property
    def upvotes(self):
        return self.votes.filter(vote_type=1).count()

    @cached_property
    def downvotes(self):
        return self.votes.filter(vote_type=-1).count()

    @cached_property
    def score(self):
        return self.votes.aggregate(total=models.Sum("vote_type"))["total"] or 0

    def get_user_vote(self, user):
        if not user.is_authenticated:
            return 0
        vote = self.votes.filter(user=user).first()
        return vote.vote_type if vote else 0


class Question(Votable, models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=256)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()
    votes = GenericRelation(Vote, related_query_name="questions")

    def __str__(self):
        return str(self.title)


class Answer(Votable, models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    votes = GenericRelation(Vote, related_query_name="answers")

    def __str__(self):
        return f"Answer by {self.author}"


class Comment(Votable, models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    answer = models.ForeignKey(
        Answer, null=True, blank=True, on_delete=models.CASCADE, related_name="comments"
    )

    parent_comment = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    votes = GenericRelation(Vote)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author}"
