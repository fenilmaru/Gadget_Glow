from django.test import TestCase
from django.contrib.auth.models import User
from orders.models import Order, OrderItem
from products.models import Product, Category


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Chargers', slug='chargers')
        self.product = Product.objects.create(name='USB Charger', price=19.99, stock=100, category=self.category)
        self.order = Order.objects.create(
            user=self.user,
            total_price=39.98,
            shipping_address='123 Test St, Test City',
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=39.98,
        )

    def test_order_creation(self):
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(str(self.order), f"Order #{self.order.id} - testuser")

    def test_order_status_default(self):
        self.assertEqual(self.order.status, 'pending')

    def test_order_items(self):
        self.assertEqual(self.order.items.count(), 1)
