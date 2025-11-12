from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UsuarioManager


# Create your models here.

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    #descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'rol'

class Permiso(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'permiso'

class RolPermiso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'rol_permiso'
        unique_together = ('rol', 'permiso')

class Usuario(AbstractUser):
    username = None
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    url_img = models.TextField(blank=True, null=True)
    estado = models.SmallIntegerField(default=1)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    fcm_token = models.TextField(blank=True, null=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']


    objects = UsuarioManager() 

    class Meta:
        db_table = 'usuario'

class Bitacora(models.Model):
    accion = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    dir_ip = models.CharField(max_length=45)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = 'bitacora'

class Administrador(models.Model):
    administrador = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    class Meta:
        db_table = 'administrador'

class Cliente(models.Model):
    cliente = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cliente'
        def __str__(self):
         return self.cliente.nombre
        
class Tecnico(models.Model):
    nombre = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    area = models.CharField(max_length=100)  # Ejemplo: "Reparaciones", "Instalaciones", etc.
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tecnico'

    def __str__(self):
        return f"{self.nombre} ({self.area})"

class Notificacion(models.Model):
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)



