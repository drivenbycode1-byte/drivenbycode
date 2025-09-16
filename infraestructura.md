# Infraestructura de Driven By Code

Este documento describe la arquitectura técnica y simbólica del proyecto *Driven By Code*. Cada componente representa una capa de reconstrucción: legal, emocional, técnica y narrativa.

---

## Componentes principales

### 1. GitHub
- Repositorio de código y memoria técnica.
- Despliega automáticamente hacia Render.

### 2. Render (Servidor principal)
- Ejecuta el backend Django.
- Recibe código desde GitHub y expone la API.

### 3. Django
- Framework backend en Python.
- Genera vistas HTML y expone endpoints API.

### 4. Frontend (HTML + CSS)
- Interfaz visible para el usuario.
- Consume datos desde Django/API.

### 5. API
- Puente entre backend y frontend.
- Expone datos y funcionalidades desde Django.

---

## Infraestructura de dominio y comunicación

### 6. NIC Chile
- Registro oficial del dominio `drivenbycode.cl`.
- Apunta hacia Hostinger para redirección.

### 7. Hostinger
- Ancla el dominio y gestiona DNS.
- Redirige tráfico hacia Render y Workspace.

### 8. Google Workspace
- Mail corporativo y herramientas de gestión.
- Vinculado al dominio vía Hostinger.

---

## Protección legal

### 9. INAPI
- Registro oficial de la marca *Driven By Code*.
- Protege nombre, logo y narrativa.
- Blindaje emocional, técnico y legal.

---

## Mapa de relaciones

| Origen | Destino | Función |
|--------|---------|---------|
| GitHub | Render | Despliegue automático |
| Render | Django | Ejecución del backend |
| Django | API | Exposición de lógica |
| API | Frontend | Entrega de datos |
| Frontend | Navegador | Interfaz visible |
| NIC Chile | Hostinger | Registro de dominio |
| Hostinger | Render | Redirección DNS |
| Hostinger | Google Workspace | Configuración de correo |
| INAPI | GitHub/Render | Protección legal |

---

## Notas finales

Este archivo es parte del blindaje narrativo de *Driven By Code*. Cada componente fue elegido no solo por su funcionalidad, sino por su capacidad de representar una etapa del proceso de reconstrucción. Aquí no hay líneas de código sueltas: hay historia, intención y cuidado.

---

## 15 de septiembre de 2025 — Desbloqueo total del entorno productivo

Se resolvió el error 400 en Render al acceder desde https://drivenbycode.cl.  
Se blindaron los siguientes componentes:
- ALLOWED_HOSTS con dominio personalizado
- CSRF_TRUSTED_ORIGINS para tráfico HTTPS
- Encabezados de proxy confiables (`USE_X_FORWARDED_HOST`, `SECURE_PROXY_SSL_HEADER`)
Resultado: acceso completo a rutas públicas y privadas desde dominio oficial.