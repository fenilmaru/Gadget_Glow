from django.test import TestCase
from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from products.models import Product, Category


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Cases', slug='cases')
        self.product = Product.objects.create(name='Phone Case', price=14.99, stock=100, category=self.category)
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertEqual(str(self.cart), f"Cart for {self.user.username}")
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.total_price, 0)

    def test_add_item(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(self.cart.total_items, 2)
        self.assertEqual(float(self.cart.total_price), 29.98)
        self.assertEqual(float(item.subtotal), 29.98)
