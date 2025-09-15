from .models import Topic

def lista_proyectos(request):
    return {'lista_proyectos': Topic.objects.all()}
