from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dbc_app.views import acceso_panel, login_oculto
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    #path('', include(tf_urls)),  # ← activa el flujo extendido con QR
    path('perro_verde_sucio/', admin.site.urls),
    path('el-perro-verde/<str:token>/', acceso_panel),
    path('acceso-silencioso/<str:token>/', login_oculto),
    path('', include('dbc_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)