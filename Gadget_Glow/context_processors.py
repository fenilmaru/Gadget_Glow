from django.conf import settings
from products.models import Category


def navbar_context(request):
    context = {'cart_count': 0, 'unread_notifications': 0, 'categories': Category.objects.filter(is_active=True)}
    if request.user.is_authenticated and not request.user.is_staff:
        try:
            from cart.models import Cart
            from notifications.models import Notification
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                context['cart_count'] = cart.total_items
            context['unread_notifications'] = Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        except Exception:
            pass
    return context
