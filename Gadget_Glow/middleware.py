import time
import logging
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger('gadget_glow')


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        return response


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()
        response = self.get_response(request)
        if request.user.is_authenticated and request.method not in ('GET', 'HEAD', 'OPTIONS'):
            duration = time.time() - request.start_time
            logger.info(
                'AUDIT: user=%s method=%s path=%s status=%s duration=%.2fs ip=%s',
                request.user.username,
                request.method,
                request.path,
                response.status_code,
                duration,
                request.META.get('REMOTE_ADDR'),
            )
        return response


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache = {}

    def __call__(self, request):
        if request.method == 'POST' and '/login' in request.path:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            now = time.time()
            window = 60
            max_attempts = 5
            key = f'login_attempts_{ip}'

            attempts = self.cache.get(key, [])
            attempts = [t for t in attempts if now - t < window]

            if len(attempts) >= max_attempts:
                logger.warning('Rate limit exceeded for IP: %s', ip)
                return HttpResponse('Too many login attempts. Try again later.', status=429)

            attempts.append(now)
            self.cache[key] = attempts

        return self.get_response(request)
