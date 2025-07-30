from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User


class AuthTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "strongpass123"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

    def test_login_valid_user(self):
        response = self.client.post(
            reverse("login"), {"username": self.username, "password": self.password}
        )
        self.assertRedirects(response, "/")

    def test_login_invalid_user(self):
        response = self.client.post(
            reverse("login"), {"username": "wrong", "password": "wrongpass"}
        )
        self.assertContains(
            response, "Please enter a correct username and password", status_code=200
        )

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse("logout"))  # must use POST
        self.assertEqual(response.status_code, 302)  # logout usually redirects

    def test_register_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "testpass1234",
                "password2": "testpass1234",
            },
        )
        self.assertRedirects(response, reverse("question_list"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
