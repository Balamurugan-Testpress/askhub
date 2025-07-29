from django.contrib.auth.models import User
from community.models import Answer, Comment
from django.utils import timezone
import random

# Fetch all users and answers
users = list(User.objects.all())
answers = list(Answer.objects.all())

if not users:
    print("No users found. Please create some users first.")
elif not answers:
    print("No answers found. Please create some answers first.")
else:
    print(f"Seeding 5 comments per answer for {len(answers)} answers...")

    for answer in answers:
        for i in range(1):
            Comment.objects.create(
                author=random.choice(users),
                content=f"This is a sample comment {i + 1} on answer for question: {answer.question.title}",
                answer=answer,
                created_at=timezone.now(),
            )

    print("✅ Seeding complete.")
