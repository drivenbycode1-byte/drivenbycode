from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Entry, Visit
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import logging
from .models import IntentoHoneypot
from .models import UserIP, Proyecto
from django.utils.timezone import now, timedelta
import os
import markdown
from pathlib import Path
from datetime import datetime


def honeypot(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', 'IP desconocida')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Agente desconocido')

    # Guardar intento en la base de datos
    IntentoHoneypot.objects.create(ip=ip, user_agent=user_agent)

    # Registrar en el log
    logger.warning(f"[HONEYPOT] Intento desde IP: {ip} | Agente: {user_agent}")

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

def home(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')).split(',')[0].strip()
    obj, created = UserIP.objects.get_or_create(ip=ip)
    obj.count += 1
    obj.last_visit = now()


    obj.save()
    return render(request, 'home.html')

def dashboard(request):
    # Total visitas
    total_visits = Visit.objects.count()
    
    # Últimas 24h
    yesterday = now() - timedelta(days=1)
    last_24h_visits = Visit.objects.filter(timestamp__gte=yesterday).count()
    
    # Visitantes únicos por IP
    unique_visits = Visit.objects.values('ip').distinct().count()
    
    # Páginas más visitadas
    popular_pages = Visit.objects.values('path').annotate(visits=Count('path')).order_by('-visits')[:10]
    
    context = {
        'total_visits': total_visits,
        'last_24h_visits': last_24h_visits,
        'unique_visits': unique_visits,
        'popular_pages': popular_pages,
    }
    return render(request, 'dbc_app/ding_dong_dashboard.html', context)

# Carpeta donde guardas tus archivos .md
CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")

def proyectos(request, dbc_id):
    # Caso especial: blog en dbc_id == 3
    if dbc_id == 3:
        posts = []
        if os.path.exists(CONTENT_DIR):
            for filename in sorted(os.listdir(CONTENT_DIR), reverse=True):
                if filename.endswith(".md"):
                    filepath = os.path.join(CONTENT_DIR, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read()
                    html = markdown.markdown(text, extensions=["extra", "nl2br"])
                    
                    # Extraer fecha del nombre del archivo (si lo nombras tipo 2025-09-21-mi-post.md)
                    try:
                        date_str = "-".join(filename.split("-")[:3])
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    except:
                        date_obj = None

                    posts.append({
                        "title": filename.replace(".md",""),
                        "text": html,
                        "data_added": date_obj
                    })

        return render(request, "dbc_app/proyecto.html", {
            "proyectos": {"id": 3, "text": "Blog"},
            "descripcion": posts
        })

    # Caso normal: usar Entry
    topic = get_object_or_404(Topic, id=dbc_id)
    entries = Entry.objects.filter(topic=topic).order_by('-data_added')
    return render(request, "dbc_app/proyecto.html", {
        "proyectos": topic,
        "descripcion": entries
    })
