from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models import User


class RegisterViewTests(APITestCase):
    def test_register_customer_success(self):
        url = reverse("register")
        data = {
            "phone": "+9779800000001",
            "email": "cust@test.com",
            "password": "testpass123",
            "role": "customer",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)
        self.assertEqual(response.data["user"]["phone"], data["phone"])
        self.assertEqual(response.data["user"]["role"], "customer")
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertTrue(User.objects.filter(phone=data["phone"]).exists())

    def test_register_shop_owner_success(self):
        url = reverse("register")
        data = {
            "phone": "+9779800000002",
            "email": "shop@test.com",
            "password": "testpass123",
            "role": "shop_owner",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["role"], "shop_owner")

    def test_register_invalid_role_rejected(self):
        url = reverse("register")
        data = {
            "phone": "+9779800000003",
            "password": "testpass123",
            "role": "admin",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_phone_rejected(self):
        User.objects.create_user(
            phone="+9779800000004", password="testpass123", role=User.Role.CUSTOMER
        )
        url = reverse("register")
        data = {
            "phone": "+9779800000004",
            "password": "otherpass123",
            "role": "customer",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="+9779800000100", password="testpass123", role=User.Role.CUSTOMER
        )
        self.url = reverse("login")

    def test_login_success(self):
        data = {"phone": self.user.phone, "password": "testpass123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["phone"], self.user.phone)

    def test_login_wrong_password_fails(self):
        data = {"phone": self.user.phone, "password": "wrongpass"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="+9779800000200", password="testpass123", role=User.Role.CUSTOMER
        )
        self.login_url = reverse("login")
        self.refresh_url = reverse("token-refresh")

    def test_token_refresh_success(self):
        login_resp = self.client.post(
            self.login_url,
            {"phone": self.user.phone, "password": "testpass123"},
            format="json",
        )
        refresh_token = login_resp.data["tokens"]["refresh"]

        response = self.client.post(
            self.refresh_url, {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotEqual(response.data["access"], login_resp.data["tokens"]["access"])


class MeViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="+9779800000300", password="testpass123", role=User.Role.CUSTOMER
        )
        self.url = reverse("me")

    def test_me_unauthenticated_fails(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_authenticated_returns_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], self.user.phone)
