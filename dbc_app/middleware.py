from django.http import HttpResponse
from django.contrib.auth import logout

class PanelFachadaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Permitir acceso al ritual silencioso
        if request.path.startswith('/acceso-silencioso/'):
            return self.get_response(request)

        # 2. Permitir acceso al login, logout y reset
        if request.path.startswith('/perro_verde_sucio/login') or request.path.startswith('/perro_verde_sucio/logout'):
            return self.get_response(request)

        # 3. ✅ Permitir acceso si el ritual fue honrado
        if request.path.startswith('/perro_verde_sucio/') and request.session.get('ritual_activado'):
            return self.get_response(request)

        # 4. Expulsión si el usuario está autenticado sin ritual
        if request.path.startswith('/perro_verde_sucio/') and request.user.is_authenticated and not request.session.get('ritual_activado'):
            logout(request)
            return HttpResponse("<h1>Autenticación anulada: el ritual no fue honrado</h1>", status=403)

        # 5. Bloqueo total si no se activó el ritual
        if request.path.startswith('/perro_verde_sucio/'):
            return HttpResponse("<h1>Acceso bloqueado: fachada activa</h1>", status=403)

        return self.get_response(request)