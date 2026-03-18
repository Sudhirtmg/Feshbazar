from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models import User
from apps.shops.models import Shop
from apps.products.models import Product, Category


def create_shop_owner():
    return User.objects.create_user(
        phone="+9779800007000",
        password="testpass123",
        role=User.Role.SHOP_OWNER,
        email="owner@test.com",
    )


def create_customer():
    return User.objects.create_user(
        phone="+9779800007001",
        password="testpass123",
        role=User.Role.CUSTOMER,
        email="cust@test.com",
    )


def create_shop(owner):
    return Shop.objects.create(
        owner=owner,
        name="Product Test Shop",
        slug="product-test-shop",
        phone="+9779800007002",
        address="Kathmandu",
        city="Kathmandu",
    )


class ProductListViewTests(APITestCase):
    def setUp(self):
        owner = create_shop_owner()
        shop = create_shop(owner)
        self.product = Product.objects.create(
            shop=shop,
            name="Chicken",
            price=Decimal("450"),
            stock_quantity=Decimal("20"),
            is_available=True,
        )
        self.unavailable = Product.objects.create(
            shop=shop,
            name="Sold Out",
            price=Decimal("100"),
            stock_quantity=Decimal("0"),
            is_available=False,
        )
        self.url = reverse("product-list")

    def test_list_returns_only_available_products(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p["name"] for p in response.data]
        self.assertIn("Chicken", names)
        self.assertNotIn("Sold Out", names)

    def test_list_filter_by_shop(self):
        response = self.client.get(
            self.url, {"shop": self.product.shop.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Chicken")


class ProductDetailViewTests(APITestCase):
    def setUp(self):
        owner = create_shop_owner()
        shop = create_shop(owner)
        self.product = Product.objects.create(
            shop=shop,
            name="Goat Meat",
            price=Decimal("600"),
            stock_quantity=Decimal("15"),
        )
        self.url = reverse("product-detail", kwargs={"pk": self.product.pk})

    def test_detail_returns_product(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Goat Meat")

    def test_detail_404_for_invalid_pk(self):
        response = self.client.get(reverse("product-detail", kwargs={"pk": 99999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProductCreateViewTests(APITestCase):
    def setUp(self):
        self.owner = create_shop_owner()
        self.shop = create_shop(self.owner)
        self.customer = create_customer()
        self.url = reverse("product-create")
        self.data = {
            "name": "New Product",
            "price": "350",
            "stock_quantity": "10",
        }

    def test_shop_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name="New Product").exists())

    def test_customer_cannot_create(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CategoryListViewTests(APITestCase):
    def setUp(self):
        Category.objects.create(name="Poultry", slug="poultry")
        Category.objects.create(name="Red Meat", slug="red-meat")
        self.url = reverse("category-list")

    def test_list_categories(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
