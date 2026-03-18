from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models import User
from apps.shops.models import Shop
from apps.products.models import Product
from apps.cart.models import Cart, CartItem


def create_customer():
    return User.objects.create_user(
        phone="+9779800006000",
        password="testpass123",
        role=User.Role.CUSTOMER,
        email="cartcust@test.com",
    )


def create_shop_with_product():
    owner = User.objects.create_user(
        phone="+9779800006001",
        password="testpass123",
        role=User.Role.SHOP_OWNER,
        email="owner@test.com",
    )
    shop = Shop.objects.create(
        owner=owner,
        name="Cart Test Shop",
        slug="cart-test-shop",
        phone="+9779800006002",
        address="Kathmandu",
        city="Kathmandu",
    )
    product = Product.objects.create(
        shop=shop,
        name="Beef",
        price=Decimal("800.00"),
        stock_quantity=Decimal("10"),
        unit=Product.Unit.KG,
    )
    return shop, product


class CartViewTests(APITestCase):
    def setUp(self):
        self.customer = create_customer()
        self.url = reverse("cart")

    def test_get_cart_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("items", response.data)
        self.assertIn("total", response.data)

    def test_get_cart_unauthenticated_fails(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_clear_cart(self):
        self.client.force_authenticate(user=self.customer)
        cart, _ = Cart.objects.get_or_create(user=self.customer)
        CartItem.objects.create(
            cart=cart,
            product=Product.objects.create(
                shop=Shop.objects.create(
                    owner=User.objects.create_user(
                        phone="+9779800006010",
                        password="x",
                        role=User.Role.SHOP_OWNER,
                    ),
                    name="X",
                    slug="x",
                    phone="1",
                    address="a",
                    city="b",
                ),
                name="P",
                price=Decimal("100"),
                stock_quantity=Decimal("5"),
            ),
            quantity=Decimal("1"),
            price_at_time=Decimal("100"),
        )
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cart.items.count(), 0)


class CartItemAddViewTests(APITestCase):
    def setUp(self):
        self.customer = create_customer()
        self.shop, self.product = create_shop_with_product()
        self.url = reverse("cart-item-add")

    def test_add_item_by_quantity_success(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            self.url,
            {"product": self.product.pk, "quantity": Decimal("2")},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["product"], self.product.pk)
        self.assertEqual(Decimal(str(response.data["quantity"])), Decimal("2"))
        self.assertTrue(CartItem.objects.filter(cart__user=self.customer).exists())

    def test_add_item_by_amount_success(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            self.url,
            {"product": self.product.pk, "amount": Decimal("400")},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_item_needs_quantity_or_amount(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            self.url,
            {"product": self.product.pk},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_out_of_stock_fails(self):
        self.product.stock_quantity = Decimal("0")
        self.product.save()
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            self.url,
            {"product": self.product.pk, "quantity": Decimal("1")},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CartItemUpdateViewTests(APITestCase):
    def setUp(self):
        self.customer = create_customer()
        self.shop, self.product = create_shop_with_product()
        self.cart, _ = Cart.objects.get_or_create(user=self.customer)
        self.item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=Decimal("2"),
            price_at_time=self.product.price,
        )

    def test_update_quantity(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("cart-item-update", kwargs={"pk": self.item.pk})
        response = self.client.patch(url, {"quantity": Decimal("3")}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, Decimal("3"))

    def test_delete_item(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("cart-item-update", kwargs={"pk": self.item.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CartItem.objects.filter(pk=self.item.pk).exists())
