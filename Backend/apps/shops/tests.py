from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models import User
from apps.shops.models import Shop


class ShopListViewTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            phone="+9779800003000",
            password="testpass123",
            role=User.Role.SHOP_OWNER,
            email="owner@test.com",
        )
        self.shop = Shop.objects.create(
            owner=self.owner,
            name="Test Meat Shop",
            slug="test-meat-shop",
            phone="+9779800003001",
            address="Thamel",
            city="Kathmandu",
            is_verified=True,
        )
        self.unverified = Shop.objects.create(
            owner=self.owner,
            name="Unverified Shop",
            slug="unverified-shop",
            phone="+9779800003002",
            address="Baluwatar",
            city="Kathmandu",
            is_verified=False,
        )
        self.url = reverse("shop-list")

    def test_list_returns_only_verified_shops(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.shop.name)

    def test_list_unauthenticated_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ShopCreateViewTests(APITestCase):
    def setUp(self):
        self.shop_owner = User.objects.create_user(
            phone="+9779800004000",
            password="testpass123",
            role=User.Role.SHOP_OWNER,
            email="owner@test.com",
        )
        self.customer = User.objects.create_user(
            phone="+9779800004001",
            password="testpass123",
            role=User.Role.CUSTOMER,
            email="cust@test.com",
        )
        self.url = reverse("shop-create")
        self.data = {
            "name": "New Butcher Shop",
            "phone": "+9779800004002",
            "address": "Thamel, Kathmandu",
            "city": "Kathmandu",
        }

    def test_shop_owner_can_create(self):
        self.client.force_authenticate(user=self.shop_owner)
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Shop.objects.filter(name=self.data["name"]).exists())

    def test_customer_cannot_create(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MyShopViewTests(APITestCase):
    def setUp(self):
        self.shop_owner = User.objects.create_user(
            phone="+9779800005000",
            password="testpass123",
            role=User.Role.SHOP_OWNER,
            email="owner@test.com",
        )
        self.shop = Shop.objects.create(
            owner=self.shop_owner,
            name="My Shop",
            slug="my-shop",
            phone="+9779800005001",
            address="Kathmandu",
            city="Kathmandu",
        )
        self.customer = User.objects.create_user(
            phone="+9779800005002",
            password="testpass123",
            role=User.Role.CUSTOMER,
            email="cust@test.com",
        )
        self.url = reverse("my-shop")

    def test_shop_owner_gets_their_shop(self):
        self.client.force_authenticate(user=self.shop_owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.shop.name)

    def test_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
