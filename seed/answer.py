from django.contrib.auth.models import User
from community.models import Question, Answer
from django.utils import timezone
import random

# Fetch all users and questions
users = list(User.objects.all())
questions = list(Question.objects.all())

if not users:
    print("No users found. Please create some users first.")
elif not questions:
    print("No questions found. Please create some questions first.")
else:
    print(f"Seeding 10 answers per question for {len(questions)} questions...")

    for question in questions:
        for i in range(10):
            Answer.objects.create(
                question=question,
                author=random.choice(users),
                content=f"This is a sample answer {i + 1} for question: {question.title}",
                created_at=timezone.now(),
            )

    print("✅ Seeding complete.")
