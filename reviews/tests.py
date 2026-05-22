from django.test import TestCase
from django.contrib.auth.models import User
from reviews.models import Review
from products.models import Product, Category


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Speakers', slug='speakers')
        self.product = Product.objects.create(name='Bluetooth Speaker', price=49.99, stock=20, category=self.category)

    def test_review_creation(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Great product!',
        )
        self.assertEqual(str(review), f"Review by {self.user.username} on {self.product.name}")
        self.assertEqual(review.rating, 5)

    def test_review_unique(self):
        Review.objects.create(product=self.product, user=self.user, rating=4, comment='Good')
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            Review.objects.create(product=self.product, user=self.user, rating=3, comment='Duplicate')
