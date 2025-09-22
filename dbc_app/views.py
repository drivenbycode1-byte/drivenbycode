from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Entry, Visit
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import logging
from .models import IntentoHoneypot
from .models import UserIP
from django.utils.timezone import now, timedelta, make_aware
from django.utils.dateparse import parse_datetime
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


CONTENT_DIR = '/path/to/indice/2'  # Ajusta la ruta a tu carpeta de markdown

def index(request):
    # Obtener los entries de la DB
    blog_entries = list(Entry.objects.filter(Q(topic__id__in=[1,2,3,4,6])))

    # Leer Markdown del contenido
    md_posts = []
    if os.path.exists(CONTENT_DIR):
        for filename in sorted(os.listdir(CONTENT_DIR), reverse=True):
            if filename.endswith('.md'):
                filepath = os.path.join(CONTENT_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if content.startswith('---'):
                    _, front_matter, text = content.split('---', 2)
                    metadata = yaml.safe_load(front_matter)
                    title = metadata.get('title', filename.replace('.md',''))
                    date_obj = metadata.get('date')
                    if date_obj:
                        date_obj = make_aware(datetime.strptime(str(date_obj), '%Y-%m-%d'))
                else:
                    title = filename.replace('.md','')
                    text = content
                    date_obj = None

                # Truncar a 85 palabras antes de convertir a HTML
                raw_excerpt = ' '.join(text.split()[:85])
                html_excerpt = markdown.markdown(raw_excerpt, extensions=['extra', 'nl2br'])
    
                md_posts.append({
                    'title': title,
                    'text': html_excerpt,
                    'data_added': date_obj,
                    'dbc_id': 2,  # si quieres usarlo en el template
                    'source': 'markdown'
                })
    
    # Combinar y ordenar por fecha
    all_entries = blog_entries + md_posts

    def get_date(entry):
        if isinstance(entry, dict):
            return entry.get('data_added') or make_aware(datetime.min)
        else:
            date_obj = getattr(entry, 'data_added', None)
            if date_obj is None:
                return make_aware(datetime.min)
            if date_obj.tzinfo is None:
                return make_aware(date_obj)
            return date_obj

    all_entries.sort(key=get_date, reverse=True)

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
    - dbc_id == 2 → proximamente.md
    - dbc_id == 3 → combatir_depresion.md
    - otros → contenido desde la base de datos
    """
    markdown_map = {
        2: "proximamente.md",
        3: "combatir_depresion.md"
    }

    if dbc_id in markdown_map:
        filename = markdown_map[dbc_id]
        filepath = os.path.join(CONTENT_DIR, filename)
        posts = []

        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Separar metadata YAML si existe
                if content.startswith('---'):
                    _, front_matter, text = content.split('---', 2)
                    metadata = yaml.safe_load(front_matter)
                    title = metadata.get("title", filename.replace(".md", ""))
                    date_obj = metadata.get("date")
                    if date_obj:
                        date_obj = datetime.strptime(str(date_obj), "%Y-%m-%d")
                else:
                    title = filename.replace(".md", "")
                    text = content
                    date_obj = None

                # Convertir a HTML solo si dbc_id == 3
                final_text = markdown.markdown(text, extensions=["extra", "nl2br"]) if dbc_id == 3 else text

            except Exception as e:
                title = filename.replace(".md", "")
                final_text = f"Error al leer el archivo: {e}"
                date_obj = None

            posts.append({
                "title": title,
                "text": final_text,
                "data_added": date_obj
            })

        context = {
            "proyectos": {"id": dbc_id, "text": "Blog" if dbc_id == 3 else "Índice"},
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
