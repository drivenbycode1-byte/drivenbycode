from django.contrib import admin
from .models import IntentoHoneypot, VisitNumber


# Register your models here.

from .models import Topic, Entry

admin.site.register(Topic)
admin.site.register(Entry)

@admin.register(IntentoHoneypot)
class IntentoHoneypotAdmin(admin.ModelAdmin):
    list_display = ('ip', 'fecha')
    readonly_fields = ('ip', 'user_agent', 'fecha')

@admin.register(VisitNumber)
class VisitNumberAdmin(admin.ModelAdmin):
    list_display = ('count', 'last_visit')
    readonly_fields = ('count', 'last_visit')

    def has_add_permission(self, request):
        return False  # ← No se crean nuevos contadores

    def has_delete_permission(self, request, obj=None):
        return False  # ← No se borra la memoria del templo


