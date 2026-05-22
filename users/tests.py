from django.test import TestCase
from django.contrib.auth.models import User
from users.models import UserProfile
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')

    def test_profile_creation(self):
        self.assertIsNotNone(self.profile)
        self.assertEqual(str(self.profile), "testuser's Profile")


class AuthAPITest(APITestCase):
    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
        }
        response = self.client.post(reverse('auth-register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)

    def test_user_login(self):
        User.objects.create_user(username='loginuser', password='testpass123')
        data = {'username': 'loginuser', 'password': 'testpass123'}
        response = self.client.post(reverse('auth-login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_login(self):
        data = {'username': 'nonexistent', 'password': 'wrongpass'}
        response = self.client.post(reverse('auth-login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
