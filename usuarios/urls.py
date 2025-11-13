from django.urls import path
from .views import (
    get_mi_perfil, login, registrar, listar_tecnicos, get_usuario_info,
    actualizar_usuario, get_tecnico_por_id, listar_usuarios, eliminar_usuario,
    get_bitacora, ver_rol, get_permisos_por_rol, actulaizar_estado_permiso,
    get_tipo_usuario_username, get_cliente_por_id, obterner_clientes,
    listar_permisos, crear_permiso, asignar_permisos_a_rol, crear_notificacion,
    listar_notificaciones, eliminar_notificacion, actualizar_token_fcm,
    crear_rol, eliminar_rol, eliminar_permiso, update_mi_perfil
)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Autenticacion y registro
    path('registro/', registrar, name='registro_usuario'),
    path('login/', login, name='login'),
    
    # Usuarios
    path('user/info/', get_usuario_info),
    path('user/<int:id>/update/', actualizar_usuario),
    path('getUser/', listar_usuarios),
    path('<int:id>/elimUser/', eliminar_usuario),
    path('clientes/', obterner_clientes),
    path('getBitacora/', get_bitacora),
    path('usuario/tipo_usuario/<str:username>/', get_tipo_usuario_username),
    path('cliente/<int:id>/info/', get_cliente_por_id),
    
    # Tecnicos
    path('tecnicos/', listar_tecnicos),
    path('tecnicos/<int:id>/info/', get_tecnico_por_id),

    # Roles
    path('rol/', ver_rol),
    path('rol/crear/', crear_rol),
    path('rol/eliminar/<int:id>/', eliminar_rol),
    path('<int:rol_id>/rol_id/rolP/', get_permisos_por_rol),
    path('actP/', actulaizar_estado_permiso),

    # Permisos
    path('permisos/', listar_permisos),
    path('permisos/crear/', crear_permiso),
    path('permisos/eliminar/<int:id>/', eliminar_permiso),
    path('permisos/asignar/', asignar_permisos_a_rol),

    # Tokens
    path('api/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),

    # Notificaciones
    path('notificaciones/', listar_notificaciones),
    path('notificaciones/crear/', crear_notificacion),
    path('notificaciones/<int:id>/eliminar/', eliminar_notificacion),
    path('fcm/update/', actualizar_token_fcm),
    
    # Perfil de clientes
    path('perfil/me/', get_mi_perfil, name='perfil_me'),
    path('user/editar/', update_mi_perfil),
]
