from django.http import HttpResponseForbidden

ALLOWED_IPS = ['181.43.202.246']  # ← Tu IP confiable

PROTECTED_PATHS = [
    '/admin/',
    '/acceso-silencioso/guardian1899/',
    '/el-perro-verde/blindajeTotal1899/',
    '/perro_verde_sucio/',
    '/reforzar-ritual/',
]

class IPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        ip = ip.split(',')[0].strip()  # ← Precisión detrás de proxy

        if ip not in ALLOWED_IPS and any(request.path.startswith(path) for path in PROTECTED_PATHS):
            return HttpResponseForbidden("Acceso denegado: IP no autorizada.")

        return self.get_response(request)