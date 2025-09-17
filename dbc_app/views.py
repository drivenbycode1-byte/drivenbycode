from django.shortcuts import render, redirect
from .models import Topic, Entry
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

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

# 🔐 Ritual de preparación: no hace login, solo redirige al inicio
def login_oculto(request, token):
    if token != 'guardian1899':
        return redirect('/')
    return redirect('/')  # Acto simbólico, sin autenticación

# 🛡️ Ritual de acceso: redirige al panel oculto para login manual
def acceso_panel(request, token):
    if token == 'blindajeTotal1899':
        return redirect('/perro_verde_sucio/')
    else:
        return redirect('/')