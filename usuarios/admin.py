from django.contrib import admin
from .models import Rol, Permiso, RolPermiso, Usuario, Administrador, Cliente, Bitacora, Notificacion

# Register your models here.
admin.site.register(Rol)
admin.site.register(Permiso)
admin.site.register(RolPermiso)
admin.site.register(Usuario)
admin.site.register(Administrador)
admin.site.register(Cliente)
admin.site.register(Bitacora)
admin.site.register(Notificacion)

