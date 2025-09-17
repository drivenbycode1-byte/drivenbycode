from django.shortcuts import render, redirect
from .models import Topic, Entry
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import logging
from .models import IntentoHoneypot

def honeypot(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', 'IP desconocida')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Agente desconocido')

    # Guardar intento en la base de datos
    IntentoHoneypot.objects.create(ip=ip, user_agent=user_agent)

    return HttpResponse("<h1>Acceso denegado: esta ruta está protegida</h1>", status=403)


def index(request):
    blog_entries = Entry.objects.filter(
        Q(topic__id=1) | Q(topic__id=2) | Q(topic__id=3) | Q(topic__id=4) | Q(topic__id=6)
    ).order_by('-data_added')[:5]
    context = {'blog_entries': blog_entries}
    return render(request, 'dbc_app/index.html', context)

def indice(request):
    indice = Topic.objects.order_by('data_added')
    context = {'indice': indice}
    return render(request, 'dbc_app/indice.html', context)

def proyectos(request, dbc_id):
    proyectos = Topic.objects.get(id=dbc_id)
    descripcion = proyectos.entry_set.order_by('data_added')
    context = {'proyectos': proyectos, 'descripcion': descripcion}
    return render(request, 'dbc_app/proyectos.html', context)

def todos_los_posts(request):
    todas_las_entradas = Entry.objects.order_by('-data_added')
    context = {'todas_las_entradas': todas_las_entradas}
    return render(request, 'dbc_app/todos_los_posts.html', context)

def login_oculto(request, token):
    if token == 'guardian1899':
        request.session['ritual_activado'] = True
        request.session.modified = True
        return redirect('/')  # ← redirige al inicio, no al panel
    return redirect('/')

def acceso_panel(request, token):
    if token == 'blindajeTotal1899' and request.session.get('ritual_activado'):
        request.session['acceso_validado_desde_blindaje'] = True
        request.session.modified = True
        return redirect('/perro_verde_sucio/')
    return HttpResponse("Acceso denegado: ritual no activado", status=403)


def reforzar_ritual_post_login(request):
    request.session['ritual_activado'] = True
    request.session.modified = True
    return redirect('/perro_verde_sucio/')

def ver_ip(request):
    ip_forwarded = request.META.get('HTTP_X_FORWARDED_FOR', 'No enviado')
    ip_remote = request.META.get('REMOTE_ADDR', 'No enviado')
    return HttpResponse(f"""
        IP via HTTP_X_FORWARDED_FOR: {ip_forwarded}<br>
        IP via REMOTE_ADDR: {ip_remote}
    """)


logger = logging.getLogger(__name__)

def honeypot(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', 'IP desconocida')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Agente desconocido')
    logger.warning(f"[HONEYPOT] Intento desde IP: {ip} | Agente: {user_agent}")
    return HttpResponse("<h1>Acceso denegado: esta ruta está protegida</h1>", status=403)


def honeypot(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', 'IP desconocida')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Agente desconocido')

    # Guardar intento en la base de datos
    IntentoHoneypot.objects.create(ip=ip, user_agent=user_agent)

    return HttpResponse("<h1>Acceso denegado: esta ruta está protegida</h1>", status=403)
