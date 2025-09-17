
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from two_factor.urls import urlpatterns as tf_urls
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from dbc_app.views import acceso_panel, login_oculto


urlpatterns = [
    path('admin/', admin.site.urls),
    path('el-perro-verde/', acceso_panel),
    path('', include(tf_urls)),
    path('', include('dbc_app.urls')),
    path('acceso-silencioso/<str:token>/', login_oculto),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)