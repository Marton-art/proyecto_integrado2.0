from django.contrib import admin
from .models import Usuario, Auditoria, Rol
from miAppCalificacion.models import Pais, Moneda

# Register your models here.
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name')

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_iso', 'moneda_local')

@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ('codigo_iso', 'nombre', 'simbolo', 'es_moneda_base')