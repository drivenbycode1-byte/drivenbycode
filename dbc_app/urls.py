
from django.urls import path
from . import views

app_name = 'dbc_app'
urlpatterns = [
    path('', views.index, name='index'),
    path('indice/', views.indice, name='indice'),
    path('indice/<int:dbc_id>', views.proyectos, name='proyectos'),
    path('todos/', views.todos_los_posts, name='todos_los_posts'),

    
    path('healthz/', views.health_check),
]