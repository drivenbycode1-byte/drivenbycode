def __call__(self, request):
    # 1. Permitir acceso al ritual silencioso
    if request.path.startswith('/acceso-silencioso/'):
        return self.get_response(request)

    # 2. Permitir acceso al login, logout y reset
    if request.path.startswith('/perro_verde_sucio/login') or request.path.startswith('/perro_verde_sucio/logout'):
        return self.get_response(request)

    # 3. ✅ Permitir acceso si el ritual fue honrado
    if request.path.startswith('/perro_verde_sucio/') and request.session.get('ritual_activado'):
        return self.get_response(request)

    # 4. Expulsión si el usuario está autenticado sin ritual
    if request.path.startswith('/perro_verde_sucio/') and request.user.is_authenticated and not request.session.get('ritual_activado'):
        logout(request)
        return HttpResponse("Autenticación anulada: el ritual no fue honrado", status=403)

    # 5. Bloqueo total si no se activó el ritual
    if request.path.startswith('/perro_verde_sucio/'):
        return HttpResponse("Acceso bloqueado: fachada activa", status=403)

    return self.get_response(request)