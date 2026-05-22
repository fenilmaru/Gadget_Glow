from django.test import TestCase
from django.contrib.auth.models import User
from ai_features.models import AIRecommendation, AIChatSession, AIChatMessage
from products.models import Product, Category


class AIModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Chargers', slug='chargers')
        self.product = Product.objects.create(
            name='Fast Charger', price=29.99, stock=50,
            category=self.category, is_featured=True,
        )
        self.session = AIChatSession.objects.create(
            user=self.user,
            session_id='test-session-001',
        )

    def test_recommendation_creation(self):
        rec = AIRecommendation.objects.create(
            user=self.user,
            product=self.product,
            score=0.95,
            reason='Top rated product',
        )
        self.assertEqual(str(rec), f"Recommendation for {self.user.username} - {self.product.name}")

    def test_chat_session(self):
        AIChatMessage.objects.create(session=self.session, role='user', content='Hello')
        AIChatMessage.objects.create(session=self.session, role='assistant', content='Hi! How can I help?')
        self.assertEqual(self.session.messages.count(), 2)
