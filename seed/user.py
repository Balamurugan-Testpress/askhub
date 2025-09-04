from django.contrib.auth import get_user_model
from account.models import UserProfile
User = get_user_model()
for user in User.objects.all():
    UserProfile.objects.get_or_create(user=user)

