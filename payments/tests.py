from django.test import TestCase
from django.contrib.auth.models import User
from payments.models import Payment, TransactionLog
from orders.models import Order, OrderItem
from products.models import Product, Category
from payments.services import create_payment, process_payment, refund_payment


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Chargers', slug='chargers')
        self.product = Product.objects.create(name='USB Cable', price=9.99, stock=100, category=self.category)
        self.order = Order.objects.create(
            user=self.user,
            total_price=9.99,
            shipping_address='123 Test St',
        )
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=9.99)

    def test_payment_creation(self):
        payment = create_payment(self.order, 9.99, 'cod', self.user)
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, 'completed')
        self.assertTrue(payment.transaction_id.startswith('TXN-'))

    def test_payment_idempotency(self):
        payment1 = create_payment(self.order, 9.99, 'cod', self.user)
        payment2 = create_payment(self.order, 9.99, 'cod', self.user)
        self.assertEqual(payment1.id, payment2.id)

    def test_transaction_log(self):
        payment = create_payment(self.order, 9.99, 'cod', self.user)
        self.assertEqual(payment.logs.count(), 1)
        self.assertEqual(payment.logs.first().action, 'created')
