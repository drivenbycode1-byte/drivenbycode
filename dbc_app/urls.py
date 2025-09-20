
from django.urls import path
from . import views
from .views import dashboard


app_name = 'dbc_app'
urlpatterns = [
    path('ver-ip/', views.ver_ip),
    path('', views.index, name='index'),
    path('indice/', views.indice, name='indice'),
    path('indice/<int:dbc_id>', views.proyectos, name='proyectos'),
    path('todos/', views.todos_los_posts, name='todos_los_posts'),
    path('ding_dong_dashboard/', dashboard, name='dashboard'),
    #path('healthz/', views.health_check),
]
