# middleware/ip_restriction.py

from django.http import HttpResponseForbidden

ALLOWED_IPS = ['181.43.202.246']  # ← Tus IPs confiables

class IPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if ip not in ALLOWED_IPS and request.path.startswith('/admin/'):
            return HttpResponseForbidden("Acceso denegado: IP no autorizada.")
        return self.get_response(request)