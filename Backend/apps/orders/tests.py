from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models import User
from apps.shops.models import Shop
from apps.products.models import Product, Category
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order
from apps.orders.api.services.status_service import advance_order_status, StatusTransitionError


def create_shop_owner():
    return User.objects.create_user(
        phone="+9779800001000",
        password="testpass123",
        role=User.Role.SHOP_OWNER,
        email="owner@shop.com",
    )


def create_customer():
    return User.objects.create_user(
        phone="+9779800002000",
        password="testpass123",
        role=User.Role.CUSTOMER,
        email="cust@test.com",
    )


def create_shop(owner):
    return Shop.objects.create(
        owner=owner,
        name="Test Butcher",
        phone="+9779800001001",
        address="Thamel, Kathmandu",
        city="Kathmandu",
        delivery_charge=Decimal("50.00"),
    )


def create_product(shop, stock=10):
    return Product.objects.create(
        shop=shop,
        name="Chicken Breast",
        price=Decimal("500.00"),
        stock_quantity=Decimal(str(stock)),
        unit=Product.Unit.KG,
    )


class CheckoutViewTests(APITestCase):
    def setUp(self):
        self.owner = create_shop_owner()
        self.customer = create_customer()
        self.shop = create_shop(self.owner)
        self.product = create_product(self.shop, stock=5)
        self.cart = Cart.objects.get_or_create(user=self.customer)[0]
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=Decimal("2"),
            price_at_time=self.product.price,
        )
        self.url = reverse("checkout")
        self.delivery_data = {
            "delivery_name": "Test User",
            "delivery_phone": "+9779800002999",
            "delivery_address": "Baluwatar, Kathmandu",
            "payment_method": "cod",
            "notes": "",
        }

    def test_checkout_success_creates_order(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, self.delivery_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        order_data = response.data[0]
        self.assertEqual(order_data["shop"], self.shop.pk)
        self.assertEqual(order_data["status"], "pending")
        self.assertEqual(Decimal(order_data["subtotal"]), Decimal("1000"))  # 2 * 500

        # Cart should be emptied
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)

        # Stock should be reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, Decimal("3"))

    def test_checkout_unauthenticated_fails(self):
        response = self.client.post(self.url, self.delivery_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_checkout_empty_cart_fails(self):
        self.cart.items.all().delete()
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, self.delivery_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("empty", response.data["detail"].lower())

    def test_checkout_insufficient_stock_fails(self):
        # Add more than available stock
        item = self.cart.items.first()
        item.quantity = Decimal("100")
        item.save()

        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, self.delivery_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stock", response.data["detail"].lower())


class OrderStatusTransitionTests(TestCase):
    def setUp(self):
        self.owner = create_shop_owner()
        self.customer = create_customer()
        self.shop = create_shop(self.owner)
        self.order = Order.objects.create(
            customer=self.customer,
            shop=self.shop,
            status=Order.Status.PENDING,
            subtotal=Decimal("1000"),
            delivery_fee=Decimal("50"),
            total_amount=Decimal("1050"),
            delivery_name="Test",
            delivery_phone="+9779800000001",
            delivery_address="Kathmandu",
        )

    def test_valid_transition_pending_to_confirmed(self):
        order = advance_order_status(
            self.order, Order.Status.CONFIRMED, changed_by=self.owner, note="Accepted"
        )
        self.assertEqual(order.status, Order.Status.CONFIRMED)
        self.assertEqual(order.history.count(), 1)
        self.assertEqual(order.history.first().to_status, Order.Status.CONFIRMED)

    def test_valid_transition_pending_to_cancelled(self):
        order = advance_order_status(
            self.order, Order.Status.CANCELLED, changed_by=self.owner
        )
        self.assertEqual(order.status, Order.Status.CANCELLED)

    def test_invalid_transition_raises_error(self):
        with self.assertRaises(StatusTransitionError) as ctx:
            advance_order_status(
                self.order, Order.Status.DELIVERED, changed_by=self.owner
            )
        self.assertIn("Cannot move", str(ctx.exception))

    def test_delivered_to_cancelled_invalid(self):
        self.order.status = Order.Status.DELIVERED
        self.order.save()
        with self.assertRaises(StatusTransitionError):
            advance_order_status(
                self.order, Order.Status.CANCELLED, changed_by=self.owner
            )
