import logging
import hashlib
import json
from datetime import datetime
from django.db import transaction
from django.conf import settings
from payments.models import Payment, TransactionLog
from Gadget_Glow.utils import generate_unique_id

logger = logging.getLogger('gadget_glow')


def generate_idempotency_key(order_id, amount):
    raw = f"{order_id}:{amount}:{datetime.now().date()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def create_payment(order, amount, method, user=None):
    idempotency_key = generate_idempotency_key(order.id, amount)
    existing = Payment.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing

    transaction_id = generate_unique_id('TXN')
    payment = Payment.objects.create(
        order=order,
        user=user or order.user,
        amount=amount,
        method=method,
        status='completed' if method == 'cod' else 'pending',
        transaction_id=transaction_id,
        idempotency_key=idempotency_key,
    )

    TransactionLog.objects.create(
        payment=payment,
        action='created',
        status=payment.status,
        details={'amount': str(amount), 'method': method}
    )

    return payment


def process_payment(payment_id, gateway_response=None):
    try:
        payment = Payment.objects.get(id=payment_id)
        payment.status = 'processing'
        payment.save()

        if gateway_response:
            payment.gateway_response = gateway_response

        payment.status = 'completed'
        payment.save()

        TransactionLog.objects.create(
            payment=payment,
            action='completed',
            status='completed',
            details={'gateway_response': gateway_response or {}}
        )

        return payment
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        payment.status = 'failed'
        payment.save()
        TransactionLog.objects.create(
            payment=payment,
            action='failed',
            status='failed',
            details={'error': str(e)}
        )
        raise


def refund_payment(payment_id):
    payment = Payment.objects.get(id=payment_id)
    payment.status = 'refunded'
    payment.save()

    TransactionLog.objects.create(
        payment=payment,
        action='refunded',
        status='refunded',
        details={'refund_date': datetime.now().isoformat()}
    )

    return payment


def get_payment_by_order(order_id):
    return Payment.objects.filter(order_id=order_id).first()
