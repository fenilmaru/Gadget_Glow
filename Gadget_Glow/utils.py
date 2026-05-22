import re
import uuid
import logging
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import exception_handler

logger = logging.getLogger('gadget_glow')


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


def generate_unique_id(prefix='GG'):
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def generate_slug(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:200]


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        errors = response.data
        if isinstance(errors, dict):
            for field, messages in errors.items():
                if isinstance(messages, list):
                    errors[field] = [str(m) for m in messages]
                else:
                    errors[field] = str(messages)
        response.data = {
            'success': False,
            'status_code': response.status_code,
            'message': str(exc) if str(exc) else 'An error occurred',
            'errors': errors,
        }
    return response


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
