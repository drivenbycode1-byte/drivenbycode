from django.http import HttpResponse

class PanelFachadaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/perro_verde_sucio/') and not request.session.get('ritual_activado'):
            return HttpResponse("Acceso bloqueado: fachada activa", status=403)
        return self.get_response(request)