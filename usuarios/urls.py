from django.urls import path, include
from . import views
from .views import get_mi_perfil,  login,registrar, listar_tecnicos,  get_usuario_info,actualizar_usuario, get_tecnico_por_id,  listar_usuarios,eliminar_usuario,get_bitacora,ver_rol ,get_permisos_por_rol,actulaizar_estado_permiso,get_tipo_usuario_username ,get_cliente_por_id,obterner_clientes,listar_permisos,crear_permiso,asignar_permisos_a_rol, crear_notificacion, listar_notificaciones,eliminar_notificacion, actualizar_token_fcm,crear_rol
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from usuarios.views import get_mi_perfil, update_mi_perfil # (o la ruta correcta a tu vista)


urlpatterns =[
    #Aautentisacion y registro
    path('registro/', registrar, name='registro_usuario'),
    path('login/', login, name='login'),
    #usuarios
    path('user/info/',get_usuario_info),
    path('user/<int:id>/update/',actualizar_usuario),
    path('getUser/',listar_usuarios),
    path('<int:id>/elimUser/',eliminar_usuario),
    path('clientes/',obterner_clientes),
    path('getBitacora/',get_bitacora),
    path('rol/',ver_rol),
    path('<int:rol_id>/rol_id/rolP/',get_permisos_por_rol),
    path('actP/',actulaizar_estado_permiso),
    path('usuario/tipo_usuario/<str:username>/',get_tipo_usuario_username),
    path('cliente/<int:id>/info/',get_cliente_por_id),
    #tecnico
    path('tecnicos/',listar_tecnicos),
    path('tecnicos/<int:id>/info/', get_tecnico_por_id),

    #permisos
    path('permisos/',listar_permisos),
    path('permisos/crear/',crear_permiso),
    path('permisos/asignar/',asignar_permisos_a_rol),
    path('rol/crear/', crear_rol),

    #path('api/token/',TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/',TokenRefreshView.as_view(), name='token_refresh'),

    #Notificasiones
    path('notificaciones/', listar_notificaciones),
    path('notificaciones/crear/', crear_notificacion),
    path('notificaciones/<int:id>/eliminar/', eliminar_notificacion),
    path('fcm/update/', actualizar_token_fcm),
    
    #clientesperfil
    path('perfil/me/', views.get_mi_perfil, name='perfil_me'),
    path('user/editar/', update_mi_perfil),
]
