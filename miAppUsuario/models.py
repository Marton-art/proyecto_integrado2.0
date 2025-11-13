from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.utils import timezone
# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    edad = models.PositiveBigIntegerField(null = True, blank = True)
    email = models.EmailField(max_length=254, unique = True)
    contraseña_hash = models.CharField(max_length=255)
    telefono = models.CharField(max_length=30,blank=True, null=True , unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=False)
    rol_usuario = models.ForeignKey(
        'Rol',
        on_delete = models.CASCADE,
        related_name = "usuarios_rol",
        verbose_name = "Rol del Sistema"
    )
    pais_usuario = models.ForeignKey(
        'miAppCalificacion.Pais',
        on_delete=models.PROTECT,
        related_name="usuarios_del_pais",
        verbose_name="País de Usuario"
    )
    
# miAppUsuario/models.py (Solo los métodos corregidos)

# ...
    
    def set_clave_secreta(self, clave_raw):
        # 🟢 CORRECCIÓN
        self.contraseña_hash = make_password(clave_raw)
        
    def check_clave_secreta(self, clave_raw):
        # 🟢 CORRECCIÓN
        return check_password(clave_raw, self.contraseña_hash)

    class Meta:
        ordering = ['nombre'] 
        # ordering hara que se ordene del nombre mas reciente al mas antiguo 
    def __str__(self):
        return f"{self.nombre} {self.apellido} <{self.email}>"
    
class Auditoria(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_VALIDATED = 'VALIDATED'
    STATUS_IMPORTING = 'IMPORTING'
    STATUS_IMPORTED = 'IMPORTED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = [
        (STATUS_PENDING,'Cargando'),
        (STATUS_VALIDATED, 'Calidando (esperando de validacion)'),
        (STATUS_IMPORTING, 'Importando.....'),
        (STATUS_IMPORTED, 'Importado'),
        (STATUS_CANCELLED, 'Proceso cancelado'),
        (STATUS_FAILED, 'Cago mano')
    ]
    uploaded_at = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='imports/', null=True, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    row_count = models.PositiveIntegerField(default=0)
    imported_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"histotico de {self.usuario} modificado en {self.modified_at}"

class Rol(models.Model):
    nombre = models.CharField(
        max_length = 50,
        unique = True,
        verbose_name = "Nombre de Rol"
    )
    descripcion = models.CharField(
        max_length =255,
        verbose_name = "Descripcion del Rol" 
    )

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']

class UsuarioHistorico(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historicos')
    
    first_name = models.CharField(max_length=100)
    
    last_name = models.CharField(max_length=100)
    
    edad = models.PositiveIntegerField(null=True, blank=True)
    
    email = models.EmailField(max_length=254)
    
    telefono = models.CharField(max_length=30, blank=True, null=True)
    
    fecha_nacimiento = models.DateField(null=True, blank=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-modified_at']
        verbose_name = "Histórico de Usuario"
        verbose_name_plural = "Históricos de Usuarios"

    def __str__(self):
        return f"Histórico de {self.usuario} modificado en {self.modified_at}"