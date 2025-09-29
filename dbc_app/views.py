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
import os, re
import markdown
import yaml
from pathlib import Path
from datetime import datetime
from django.conf import settings
from unicodedata import normalize



def honeypot(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', 'IP desconocida')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Agente desconocido')

    # Guardar intento en la base de datos
    IntentoHoneypot.objects.create(ip=ip, user_agent=user_agent)

    # Registrar en el log
    logger.warning(f"[HONEYPOT] Intento desde IP: {ip} | Agente: {user_agent}")

    return HttpResponse("<h1>Acceso denegado: esta ruta está protegida</h1>", status=403)


CONTENT_DIR = os.path.join(settings.BASE_DIR, "content")

def index(request):
    TITULOS_POR_ID = {
        1: "SpiritInMotion",
        2: "Antes de Rendirte",
        3: "Blog",
        4: "Preguntas y Comunidad",
        5: "Sobre mí",
        6: "Proyectos"
    }

    md_posts = []
    tags_disponibles = set()

    if os.path.exists(CONTENT_DIR):
        for folder in os.listdir(CONTENT_DIR):
            folder_path = os.path.join(CONTENT_DIR, folder)
            if os.path.isdir(folder_path):
                # Detectar dbc_id desde el nombre de carpeta
                match = re.search(r'indice[_/]?(\d+)', folder)
                dbc_id = int(match.group(1)) if match else 0

                for filename in sorted(os.listdir(folder_path), reverse=True):
                    if filename.endswith('.md'):
                        filepath = os.path.join(folder_path, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()

                            # Extraer metadatos
                            if content.startswith('---'):
                                _, front_matter, text = content.split('---', 2)
                                metadata = yaml.safe_load(front_matter)
                                title = metadata.get('title', filename.replace('.md', ''))
                                summary = metadata.get('summary', '')
                                date_raw = metadata.get('date')
                                try:
                                    date_obj = make_aware(datetime.strptime(str(date_raw), '%Y-%m-%d')) if date_raw else None
                                except:
                                    date_obj = None
                                tags = metadata.get('tags')
                                if not isinstance(tags, list):
                                    tags = []
                            else:
                                title = filename.replace('.md', '')
                                text = content
                                date_obj = None
                                tags = []
                                summary = ''

                            tags_disponibles.update(tags)

                            # Generar excerpt
                            raw_excerpt = ' '.join(text.split()[:85])
                            html_excerpt = markdown.markdown(raw_excerpt, extensions=['extra', 'nl2br'])

                            
                            # Validar entrada útil
                            if title and html_excerpt:
                                md_posts.append({
                                    'title': title,
                                    'text': html_excerpt,
                                    'data_added': date_obj,
                                    'dbc_id': dbc_id,
                                    'source': 'markdown',
                                    'tags': tags,
                                    'summary': summary
                                })

                        except Exception:
                            continue

    # Ordenar por fecha
    def get_date(entry):
        return entry.get('data_added') or make_aware(datetime.min)

    all_entries = sorted(md_posts, key=get_date, reverse=True)

    context = {
        'blog_entries': all_entries,
        'tags_disponibles': sorted(tags_disponibles),
        'titulos_por_id': TITULOS_POR_ID
    }

    return render(request, 'dbc_app/index.html', context)



def indice(request):
    indice = Topic.objects.order_by('data_added')
    context = {'indice': indice}
    return render(request, 'dbc_app/indice.html', context)

def todos_los_posts(request):
    TITULOS_POR_ID = {
        1: "SpiritInMotion",
        2: "Antes de Rendirte",
        3: "Blog",
        4: "Preguntas y Comunidad",
        5: "Sobre mí",
        6: "Proyectos"
    }

    md_posts = []

    if os.path.exists(CONTENT_DIR):
        for folder in os.listdir(CONTENT_DIR):
            folder_path = os.path.join(CONTENT_DIR, folder)
            if os.path.isdir(folder_path):
                match = re.search(r'indice[_/]?(\d+)', folder)
                dbc_id = int(match.group(1)) if match else 0

                for filename in sorted(os.listdir(folder_path), reverse=True):
                    if filename.endswith('.md'):
                        filepath = os.path.join(folder_path, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()

                            if content.startswith('---'):
                                _, front_matter, text = content.split('---', 2)
                                metadata = yaml.safe_load(front_matter)
                                title = metadata.get('title', filename.replace('.md', ''))
                                summary = metadata.get('summary', '')
                                date_raw = metadata.get('date')
                                try:
                                    date_obj = make_aware(datetime.strptime(str(date_raw), '%Y-%m-%d')) if date_raw else None
                                except:
                                    date_obj = None
                                tags = metadata.get('tags')
                                if not isinstance(tags, list):
                                    tags = []
                            else:
                                title = filename.replace('.md', '')
                                text = content
                                date_obj = None
                                tags = []
                                summary = ''

                            raw_excerpt = ' '.join(text.split()[:85])
                            html_excerpt = markdown.markdown(raw_excerpt, extensions=['extra', 'nl2br'])

                            if title and raw_excerpt.strip():
                                md_posts.append({
                                    'title': title,
                                    'text': html_excerpt,
                                    'data_added': date_obj,
                                    'dbc_id': dbc_id,
                                    'tags': tags,
                                    'summary': summary
                                })

                        except Exception:
                            continue

    # Ordenar por fecha
    def get_date(entry):
        return entry.get('data_added') or make_aware(datetime.min)

    todas_las_entradas = sorted(md_posts, key=get_date, reverse=True)

    context = {
        'todas_las_entradas': todas_las_entradas,
        'titulos_por_id': TITULOS_POR_ID
    }

    return render(request, 'dbc_app/todos_los_posts.html', context)


def posts_por_tag(request, tag):
    """
    Muestra todos los posts (Markdown o Entry) que contienen el tag especificado.
    """
    posts = []
    tag = normalize("NFKD", tag).encode("ascii", "ignore").decode("utf-8").lower()
    # Buscar en archivos Markdown
    for folder in os.listdir(CONTENT_DIR):
        folder_path = os.path.join(CONTENT_DIR, folder)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".md"):
                    filepath = os.path.join(folder_path, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()

                        if content.startswith('---'):
                            _, front_matter, text = content.split('---', 2)
                            metadata = yaml.safe_load(front_matter)
                            tags = metadata.get("tags", [])
                            if tag in [normalize("NFKD", t).encode("ascii", "ignore").decode("utf-8").lower() for t in tags]:
                                title = metadata.get("title", filename.replace(".md", ""))
                                date_obj = metadata.get("date")
                                if date_obj:
                                    date_obj = datetime.strptime(str(date_obj), "%Y-%m-%d")
                                final_text = markdown.markdown(text, extensions=["extra", "nl2br"])
                                posts.append({
                                    "title": title,
                                    "text": final_text,
                                    "data_added": date_obj,
                                    "tags": tags,
                                    "summary": metadata.get("summary", ""),
                                    "source": "markdown"
                                })
                    except:
                        continue

    # Opcional: buscar también en Entry si usas tags ahí

    posts.sort(key=lambda x: x["data_added"] or datetime.min, reverse=True)

    context = {
        "tag": tag,
        "posts": posts
    }
    return render(request, "dbc_app/posts_por_tag.html", context)

def seccion_por_id(request, seccion_id):
    from django.utils.timezone import make_aware
    import os, yaml, markdown
    from datetime import datetime

    folder_name = f"indice_{seccion_id}"
    folder_path = os.path.join(CONTENT_DIR, folder_name)

    posts = []

    if os.path.exists(folder_path):
        for filename in sorted(os.listdir(folder_path), reverse=True):
            if filename.endswith('.md'):
                filepath = os.path.join(folder_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if content.startswith('---'):
                        _, front_matter, text = content.split('---', 2)
                        metadata = yaml.safe_load(front_matter)
                        title = metadata.get('title', filename.replace('.md', ''))
                        summary = metadata.get('summary', '')
                        date_raw = metadata.get('date')
                        try:
                            date_obj = make_aware(datetime.strptime(str(date_raw), '%Y-%m-%d')) if date_raw else None
                        except:
                            date_obj = None
                    else:
                        title = filename.replace('.md', '')
                        summary = ''
                        date_obj = None

                    posts.append({
                        'title': title,
                        'summary': summary,
                        'filename': filename,
                        'seccion_id': seccion_id,
                        'data_added': date_obj
                    })

                except Exception:
                    continue

    posts.sort(key=lambda x: x['data_added'] or make_aware(datetime.min), reverse=True)

    TITULOS_POR_ID = {
        1: "SpiritInMotion",
        2: "Antes de Rendirte",
        3: "Blog",
        4: "Preguntas y Comunidad",
        5: "Sobre mí",
        6: "Proyectos"
    }

    context = {
        'posts': posts,
        'seccion_id': seccion_id,
        'seccion_titulo': TITULOS_POR_ID.get(seccion_id, f"Sección {seccion_id}")
    }

    return render(request, 'dbc_app/seccion_por_id.html', context)



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
    TITULOS_PERSONALIZADOS = {
        1: "SpiritInMotion",
        2: "Antes de Rendirte",
        3: "Blog",
        4: "Preguntas y Comunidad",
        5: "Sobre mí",
        6: "Proyectos"
    }

    folder_path = os.path.join(CONTENT_DIR, f"indice_{dbc_id}")
    posts = []

    if os.path.isdir(folder_path):
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".md"):
                filepath = os.path.join(folder_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    if content.startswith('---'):
                        _, front_matter, text = content.split('---', 2)
                        metadata = yaml.safe_load(front_matter)
                        title = metadata.get("title", filename.replace(".md", ""))
                        date_obj = metadata.get("date")
                        if date_obj:
                            date_obj = datetime.strptime(str(date_obj), "%Y-%m-%d")
                        summary = metadata.get("summary", "")
                    else:
                        title = filename.replace(".md", "")
                        text = content
                        date_obj = None
                        summary = ""

                    final_text = markdown.markdown(text, extensions=["extra", "nl2br"])

                    posts.append({
                        "title": title,
                        "text": final_text,
                        "data_added": date_obj,
                        "source": "markdown",
                        "dbc_id": dbc_id,
                        "summary": summary
                    })

                except Exception as e:
                    posts.append({
                        "title": filename.replace(".md", ""),
                        "text": f"Error al leer el archivo: {e}",
                        "data_added": None,
                        "source": "markdown",
                        "dbc_id": dbc_id,
                        "summary": ""
                    })

        posts.sort(key=lambda x: x["data_added"] or datetime.min, reverse=True)

    else:
        topic = get_object_or_404(Topic, id=dbc_id)
        entries = Entry.objects.filter(topic=topic).order_by('-data_added')
        for entry in entries:
            posts.append(entry)

    context = {
        "proyectos": {
            "id": dbc_id,
            "text": TITULOS_PERSONALIZADOS.get(dbc_id, "Índice")
        },
        "descripcion": posts
    }

    return render(request, "dbc_app/proyectos.html", context)
