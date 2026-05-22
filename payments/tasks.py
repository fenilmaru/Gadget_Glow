from celery import shared_task
from payments.models import Payment
from payments.services import process_payment
import logging

logger = logging.getLogger('gadget_glow')


@shared_task
def process_pending_payment(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        if payment.status == 'pending':
            process_payment(payment_id)
            logger.info(f"Payment {payment_id} processed")
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found")
