from django.test import TestCase
from products.models import Category, Brand, Product
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Chargers', slug='chargers')
        self.brand = Brand.objects.create(name='Anker', slug='anker')
        self.product = Product.objects.create(
            name='Fast Charger',
            price=29.99,
            stock=50,
            category=self.category,
            brand=self.brand,
        )

    def test_category_creation(self):
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(str(self.category), 'Chargers')

    def test_brand_creation(self):
        self.assertEqual(Brand.objects.count(), 1)
        self.assertEqual(str(self.brand), 'Anker')

    def test_product_creation(self):
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(str(self.product), 'Fast Charger')
        self.assertEqual(self.product.discount_percentage, 0)
        self.assertTrue(self.product.in_stock)

    def test_available_stock(self):
        self.assertEqual(self.product.available_stock, 50)
        self.product.reserved_stock = 5
        self.product.save()
        self.assertEqual(self.product.available_stock, 45)

    def test_discount_calculation(self):
        self.product.compare_price = 49.99
        self.product.save()
        self.assertEqual(self.product.discount_percentage, 40)


class ProductAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Earphones', slug='earphones')
        Product.objects.create(name='Wireless Buds', price=79.99, stock=30, category=self.category)

    def test_list_products(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_featured_products(self):
        response = self.client.get('/api/v1/products/featured/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
