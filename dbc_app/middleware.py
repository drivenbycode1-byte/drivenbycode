from django.http import HttpResponse
from django.contrib.auth import logout

class PanelFachadaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Permitir acceso al login
        if request.path.startswith('/perro_verde_sucio/login'):
            return self.get_response(request)

        # Bloqueo si el ritual no está activo
        if request.path.startswith('/perro_verde_sucio/') and not request.session.get('ritual_activado'):
            return HttpResponse("Acceso bloqueado: fachada activa", status=403)

        # Expulsión si el usuario está autenticado pero el ritual ya fue consumido
        if request.path.startswith('/perro_verde_sucio/') and request.user.is_authenticated and not request.session.get('ritual_activado'):
            logout(request)
            return HttpResponse("Autenticación anulada: el ritual ya fue honrado", status=403)

        return self.get_response(request)