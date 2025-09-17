from django.http import HttpResponse
from django.contrib.auth import logout

class PanelFachadaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Permitir acceso al login, logout y reset
        if request.path.startswith('/perro_verde_sucio/login') or request.path.startswith('/perro_verde_sucio/logout'):
            return self.get_response(request)

        # Bloqueo total si no se activó el ritual
        if request.path.startswith('/perro_verde_sucio/') and not request.session.get('ritual_activado'):
            return HttpResponse("Acceso bloqueado: fachada activa", status=403)

        # Expulsión si el usuario está autenticado sin ritual
        if request.path.startswith('/perro_verde_sucio/') and request.user.is_authenticated and not request.session.get('ritual_activado'):
            logout(request)
            return HttpResponse("Autenticación anulada: el ritual no fue honrado", status=403)

        return self.get_response(request)