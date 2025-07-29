import random
from django.contrib.auth.models import User
from community.models import Question
from taggit.models import Tag

# Create users
users = []
for i in range(1, 6):
    username = f"user{i}"
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("#123@123")
        user.save()
        print(f"✅ Created user: {username}")
    else:
        print(f"ℹ️ User already exists: {username}")
    users.append(user)

# Define realistic tags
tag_names = [
    "django",
    "python",
    "html",
    "css",
    "bootstrap",
    "javascript",
    "api",
    "database",
    "debugging",
    "deployment",
    "auth",
    "queryset",
]

# Create tags
for tag_name in tag_names:
    Tag.objects.get_or_create(name=tag_name)

# Sample question pool (title, desc)
question_pool = [
    (
        "How to filter a queryset in Django?",
        "I want to filter my queryset based on multiple tags and search keywords. How can I achieve this in Django CBV?",
    ),
    (
        "What is the use of taggit in Django?",
        "Can someone explain how to use django-taggit for tagging content like blog posts or questions?",
    ),
    (
        "Difference between filter and get in Django ORM",
        "What is the functional difference between using `filter()` and `get()` in Django queries?",
    ),
    (
        "How to implement authentication in Django?",
        "I want to build a login/logout system. Should I use Django's built-in auth or a custom one?",
    ),
    (
        "Best practices for Django model design",
        "What are some model design tips for building scalable Django applications?",
    ),
    (
        "How to use Bootstrap with Django templates?",
        "I’m new to Bootstrap. How can I link it correctly with my Django project and make the UI responsive?",
    ),
    (
        "Debugging tips for Django projects",
        "What tools and techniques do you use to debug Django applications efficiently?",
    ),
    (
        "How to connect PostgreSQL with Django?",
        "Can anyone share the steps to connect PostgreSQL and configure it with Django settings?",
    ),
    (
        "Deploying Django app to production",
        "What is the best way to deploy a Django app on a server using Gunicorn and Nginx?",
    ),
    (
        "What are Django CBVs and FBVs?",
        "Can someone explain the difference between Class Based Views and Function Based Views with examples?",
    ),
]

# Create 50 questions, 10 per user
count = 0
for user in users:
    for _ in range(10):
        title, description = random.choice(question_pool)
        count += 1
        question = Question.objects.create(
            author=user,
            title=f"{title} #{count}",
            description=description,
        )
        # Assign 2–4 random tags
        tags_for_question = random.sample(tag_names, k=random.randint(2, 4))
        question.tags.add(*tags_for_question)
        print(f"📝 Created: {question.title} | Tags: {', '.join(tags_for_question)}")

print("✅ 50 questions created with tags.")
