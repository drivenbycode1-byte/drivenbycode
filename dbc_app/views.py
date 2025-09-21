from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Entry, Visit
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import logging
from .models import IntentoHoneypot
from .models import UserIP
from django.utils.timezone import now, timedelta
import os
import markdown
import yaml
from pathlib import Path
from datetime import datetime
from django.conf import settings



def honeypot(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', 'IP desconocida')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Agente desconocido')

    # Guardar intento en la base de datos
    IntentoHoneypot.objects.create(ip=ip, user_agent=user_agent)

    # Registrar en el log
    logger.warning(f"[HONEYPOT] Intento desde IP: {ip} | Agente: {user_agent}")

    return HttpResponse("<h1>Acceso denegado: esta ruta está protegida</h1>", status=403)


def index(request):
    from datetime import datetime
    import os, yaml, markdown

    blog_entries = list(Entry.objects.filter(
        Q(topic__id__in=[1,2,3,4,6])
    ).order_by('-data_added')[:5])

    # Leer Markdown del contenido
    CONTENT_DIR = os.path.join(BASE_DIR, 'content')  # Ajusta tu path
    md_posts = []
    if os.path.exists(CONTENT_DIR):
        for filename in sorted(os.listdir(CONTENT_DIR), reverse=True):
            if filename.endswith(".md"):
                filepath = os.path.join(CONTENT_DIR, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if content.startswith('---'):
                    _, front_matter, text = content.split('---', 2)
                    metadata = yaml.safe_load(front_matter)
                    title = metadata.get("title", filename.replace(".md",""))
                    date_obj = metadata.get("date")
                    if date_obj:
                        date_obj = datetime.strptime(str(date_obj), "%Y-%m-%d")
                else:
                    title = filename.replace(".md","")
                    text = content
                    date_obj = None

                html = markdown.markdown(text, extensions=["extra", "nl2br"])
                md_posts.append({
                    "title": title,
                    "text": html,
                    "data_added": date_obj
                })

    # Combinar y ordenar por fecha
    all_entries = blog_entries + md_posts
    all_entries.sort(key=lambda x: getattr(x, 'data_added', x.get('data_added', datetime.min)), reverse=True)

    context = {'blog_entries': all_entries}
    return render(request, 'dbc_app/index.html', context)

def indice(request):
    indice = Topic.objects.order_by('data_added')
    context = {'indice': indice}
    return render(request, 'dbc_app/indice.html', context)

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


CONTENT_DIR = os.path.join(settings.BASE_DIR, "dbc_app", "content")


def proyectos(request, dbc_id):
    """
    Vista para mostrar un Topic o archivos Markdown especiales.
    - dbc_id == 3 → blog
    - dbc_id == 2 → índice desde Markdown
    - otros → Entry del Topic
    """
    # Diccionario que mapea dbc_id a archivo Markdown
    markdown_map = {
        2: "indice2.md",
        3: None  # blog lee todos los .md en CONTENT_DIR
    }

    # Casos especiales Markdown
    if dbc_id in markdown_map:
        posts = []
        if dbc_id == 3:
            files = sorted(os.listdir(CONTENT_DIR), reverse=True)
        else:
            filename = markdown_map[dbc_id]
            files = [filename] if filename and os.path.exists(os.path.join(CONTENT_DIR, filename)) else []

        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(CONTENT_DIR, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    # Separar metadata YAML si existe
                    if content.startswith('---'):
                        _, front_matter, text = content.split('---', 2)
                        metadata = yaml.safe_load(front_matter)
                        title = metadata.get("title", file.replace(".md",""))
                        date_obj = metadata.get("date")
                        if date_obj:
                            date_obj = datetime.strptime(str(date_obj), "%Y-%m-%d")
                    else:
                        title = file.replace(".md","")
                        text = content
                        date_obj = None

                    html = markdown.markdown(text, extensions=["extra", "nl2br"])
                except Exception as e:
                    html = f"<p>Error al leer el archivo: {e}</p>"
                    title = file.replace(".md","")
                    date_obj = None

                posts.append({
                    "title": title,
                    "text": html,
                    "data_added": date_obj
                })

        context = {
            "proyectos": {"id": dbc_id, "text": "Blog" if dbc_id==3 else "Índice"},
            "descripcion": posts
        }
        return render(request, "dbc_app/proyectos.html", context)

    # Caso normal: usar Entry del Topic
    topic = get_object_or_404(Topic, id=dbc_id)
    entries = Entry.objects.filter(topic=topic).order_by('-data_added')
    context = {
        "proyectos": topic,
        "descripcion": entries
    }
    return render(request, "dbc_app/proyectos.html", context)
