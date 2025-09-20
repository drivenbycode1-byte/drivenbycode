from dbc_app.models import Visit
from django.db.utils import OperationalError

class TrackVisitsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(('/admin', '/static')):
            try:
                ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
                ip = ip.split(',')[0].strip()
                Visit.objects.create(
                    ip=ip,
                    path=request.path,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
            except OperationalError:
                # La tabla no existe todavía, ignora por ahora
                pass
        return self.get_response(request)
