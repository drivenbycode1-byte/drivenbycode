from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from dbc_app.models import VisitNumber

class VisitCounterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.get('visited'):
            visit, _ = VisitNumber.objects.get_or_create(id=1)
            visit.count += 1
            visit.last_visit = now()
            visit.save()
            request.session['visited'] = True