from .models import Visit

class TrackVisitsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Filtra URLs que quieres trackear (evita admin, static, etc.)
        if not request.path.startswith(('/admin', '/static')):
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            ip = ip.split(',')[0].strip()  # Precisión detrás de proxy
            Visit.objects.create(
                ip=ip,
                path=request.path,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
        response = self.get_response(request)
        return response
