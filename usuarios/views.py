from django.shortcuts import render
from .models import Usuario, Permiso, Rol, RolPermiso, Bitacora, Cliente, Notificacion, Tecnico
from .serializers import UsuarioSerializers, BitacoraSerializers, UsuarioAdminUpdateSerializers, RolSerializers, NotificacionSerializers
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta, timezone
from .utils import get_client_ip
from django.conf import settings
import jwt
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .serializers import TecnicoSerializer
# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def registrar(request):
    serializer = UsuarioSerializers(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()
        res=UsuarioSerializers(usuario)
        registrar_bitacora(request,f'registro {usuario.rol.nombre}',usuario)
        return Response({
            'mensaje': 'Usuario registrado exitosamente.',
            'usuario': res.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def registrar_bitacora(request, accion, usuario):
    ip = get_client_ip(request)
    Bitacora.objects.create(
        dir_ip=ip,
        accion=accion,
        usuario=usuario
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email y contraseña son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(email=email, estado=1)
    except Usuario.DoesNotExist:
        return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(password, usuario.password):
        return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

    # ✅ Generar tokens válidos (access + refresh)
    refresh = RefreshToken.for_user(usuario)

    # Obtener permisos del rol
    permisos = Permiso.objects.filter(
        rolpermiso__rol=usuario.rol,
        rolpermiso__estado=True
    ).values_list('nombre', flat=True)

    # Registrar bitácora (opcional)
    ip = get_client_ip(request)
    from .models import Bitacora
    Bitacora.objects.create(
        accion='inicio sesion',
        dir_ip=ip,
        usuario=usuario
    )

    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol.nombre.upper() if usuario.rol else "SIN_ROL",
            "rol_id": usuario.rol.id if usuario.rol else None,
            "permisos": list(permisos),
        }
    }, status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_usuario(request, id):
    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UsuarioAdminUpdateSerializers(usuario, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        registrar_bitacora(request, f'actualizó usuario {usuario.nombre}', usuario)
        return Response({
            'mensaje': 'Usuario actualizado exitosamente.',
            'usuario': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_usuario_info(request):
    """
    Devuelve la información del usuario autenticado usando el token JWT.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'error': 'Token no proporcionado'}, status=401)
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        usuario = Usuario.objects.get(id=user_id)
        
        return Response({
            'id': usuario.id,
            'nombre': usuario.nombre,
            'email': usuario.email,
            'telefono': usuario.telefono,
            'direccion': usuario.direccion,
            'url_img': usuario.url_img,
            'estado': usuario.estado,
            'rol': usuario.rol.nombre if usuario.rol else None,
            'rol_id': usuario.rol.id if usuario.rol else None
        }, status=200)
    
    except jwt.ExpiredSignatureError:
        return Response({'error': 'El token ha expirado'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'error': 'Token inválido'}, status=401)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)

def get_usuario_info_desde_token_manual(request):
    auth_header = request.headers.get('Authorization')
    print(auth_header)
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        usuario = Usuario.objects.get(id=user_id)
        return usuario
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Usuario.DoesNotExist):
        return None
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_usuarios(request):
    Usuarios = Usuario.objects.filter(estado=True).order_by('id')
    serializer = UsuarioSerializers(Usuarios, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obterner_clientes(request):
    clientes = Usuario.objects.filter(rol = 2).order_by('id')
    serializer = UsuarioSerializers(clientes, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_usuario(request, id):
    try:
        usuario = Usuario.objects.get(id=id, estado = True)
        usuario.estado = False
        usuario.save()  
        info = get_usuario_info_desde_token_manual(request)
        registrar_bitacora(request, 'eliminino usuario', info)
        return Response({'mensaje': 'Usuario eliminado exitosamente.'}, status=status.HTTP_200_OK)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_rol(request):
    roles = Rol.objects.all()
    serializer = RolSerializers(roles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_permisos_por_rol(request, rol_id):
    try:
        rol = Rol.objects.get(id=rol_id)
    except Rol.DoesNotExist:
        return Response({'error': 'Rol no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    # permisos asociados
    rol_permiso = RolPermiso.objects.filter(rol_id=rol_id).values(
        'permiso__id', 'permiso__nombre', 'estado'
    )

    data = [
        {
            'permiso_id': rp['permiso__id'],
            'permiso_nombre': rp['permiso__nombre'],
            'estado': rp['estado']
        }
        for rp in rol_permiso
    ]

    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_permiso(request):
    nombre = request.data.get('nombre')
    
    if not nombre:
        return Response({'error': 'El campo nombre es requerido.'},status=status.HTTP_400_BAD_REQUEST)
    if Permiso.objects.filter(nombre=nombre).exists():
        return Response({'error': 'Ya existe un permiso con ese nombre.'},status=status.HTTP_400_BAD_REQUEST)
    
    permiso = Permiso.objects.create(nombre=nombre)
    return Response({
        'mensaje': 'Permiso creado correctamente.','permiso': {'id': permiso.id, 'nombre': permiso.nombre}}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_permisos(requets):
    permiso = Permiso.objects.all().values('id','nombre')
    return Response(list(permiso),status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asignar_permisos_a_rol(request):
    rol_id = request.data.get('rol_id')
    permisos_ids = request.data.get('permisos')  # lista de IDs

    if not rol_id or not isinstance(permisos_ids, list):
        return Response({'error': 'rol_id y lista de permisos son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rol = Rol.objects.get(id=rol_id)
    except Rol.DoesNotExist:
        return Response({'error': 'Rol no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    asignados = []
    for pid in permisos_ids:
        permiso = Permiso.objects.get(id=pid)
        obj, created = RolPermiso.objects.update_or_create(
            rol=rol, permiso=permiso,
            defaults={'estado': True}
        )
        asignados.append({'permiso': permiso.nombre, 'nuevo': created})

    return Response({
        'mensaje': 'Permisos asignados correctamente.',
        'rol': rol.nombre,
        'permisos': asignados
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actulaizar_estado_permiso(request):
    rol_id = request.data.get('rol_id')
    Permiso = request.data.get('permisos')

    if rol_id is None or not isinstance(Permiso, list):
        return Response({'error': 'Se requiere rol_id y lista de permisos'},status=status.HTTP_400_BAD_REQUEST)
    errores =[]
    actualizados = 0

    for p in Permiso:
        permiso_id = p.get('permiso_id')
        estado =p.get('estado')

        if permiso_id is None or estado is None:
            errores.append(f"Faltan datos en permiso {p}")
            continue
        updated = RolPermiso.objects.filter(rol_id=rol_id, permiso_id=permiso_id).update(estado=estado)
        if updated == 0:
            errores.append(f"No existe relación con permiso_id {permiso_id}")
        else:
            actualizados += 1

    return Response({
        'mensaje': f'{actualizados} permisos actualizados',
        'errores': errores
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bitacora(request):
    """
    Devuelve todas las acciones registradas en bitácora junto con información del usuario.
    """
    bitacora = (
        Bitacora.objects
        .select_related('usuario', 'usuario__rol')  # 🔹 Esto asegura que traiga el nombre, correo y rol
        .all()
        .order_by('-fecha_hora')
    )

    serializer = BitacoraSerializers(bitacora, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tipo_usuario_username(request, username):
    try:
        usuario = Usuario.objects.get(email=username)
        return Response({'tipo_usuario': usuario.rol.nombre}, status=200)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cliente_por_id(request, id):
    try:
        usuario = Usuario.objects.get(id=id, estado=1)
        cliente = Cliente.objects.get(cliente=usuario)

        if usuario.rol.nombre.lower() != "cliente":
            return Response({"error": "El usuario no es un cliente"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "id_cliente": cliente.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "telefono": usuario.telefono,
            "direccion": usuario.direccion,
            "rol": usuario.rol.nombre
        }, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Cliente.DoesNotExist:
        return Response({"error": "No se encontró registro en la tabla cliente"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_notificacion(request):
    try:
        titulo = request.data.get('titulo')
        mensaje = request.data.get('mensaje')
        usuario_id = request.data.get('usuario_id')

        # Validar campos
        if not titulo or not mensaje or not usuario_id:
            return Response(
                {'error': 'Todos los campos son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar usuario
        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': f'Usuario con id={usuario_id} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Guardar en base de datos
        noti = Notificacion.objects.create(
            titulo=titulo,
            mensaje=mensaje,
            usuario=usuario
        )

        # Enviar push
        enviar_notificacion_push(usuario, titulo, mensaje)

        return Response({
            'mensaje': 'Notificación enviada correctamente.',
            'data': {
                'id': noti.id,
                'titulo': noti.titulo,
                'mensaje': noti.mensaje,
                'usuario': usuario.nombre if hasattr(usuario, 'nombre') else usuario.email
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_notificaciones(request):
    user_id = request.query_params.get('user_id')

    if user_id:
        notificaciones = Notificacion.objects.filter(usuario_id=user_id).order_by('-fecha_envio')
    else:
        notificaciones = Notificacion.objects.all().order_by('-fecha_envio')

    serializer = NotificacionSerializers(notificaciones, many=True)
    return Response(serializer.data, status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_notificacion(request, id):
    try:
        notificacion = Notificacion.objects.get(id=id)
        notificacion.delete()
        return Response({'mensaje': 'Notificación eliminada correctamente.'}, status=200)
    except Notificacion.DoesNotExist:
        return Response({'error': 'Notificación no encontrada.'}, status=404)

#Metodo PUSH
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def actualizar_token_fcm(request):
    token = request.data.get('fcm_token')
    usuario = get_usuario_info_desde_token_manual(request)
    if not usuario:
        return Response({'error': 'Usuario no autenticado'}, status=401)

    usuario.fcm_token = token
    usuario.save()
    return Response({'mensaje': 'Token FCM actualizado correctamente'}, status=200)



from pyfcm import FCMNotification
from django.conf import settings

def enviar_notificacion_push(usuario, titulo, mensaje):
    if not usuario.fcm_token:
        print(f"El usuario {usuario.email} no tiene token FCM registrado.")
        return

    push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)
    result = push_service.notify_single_device(
        registration_id=usuario.fcm_token,
        message_title=titulo,
        message_body=mensaje,
        sound="default"
    )
    print("Notificación enviada:", result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_rol(request):
    serializer = RolSerializers(data=request.data)
    if serializer.is_valid():
        # Evitar duplicados
        nombre = serializer.validated_data.get('nombre')
        if Rol.objects.filter(nombre__iexact=nombre).exists():
            return Response(
                {'error': 'Ya existe un rol con ese nombre.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response({
            'mensaje': 'Rol creado exitosamente.',
            'rol': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_rol(request, id):
    try:
        rol = Rol.objects.get(id=id)
        # Verificar que no sea el rol de Administrador (protección)
        if rol.id == 1:
            return Response(
                {'error': 'No se puede eliminar el rol de Administrador.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        rol.delete()
        return Response(
            {'mensaje': 'Rol eliminado correctamente.'},
            status=status.HTTP_200_OK
        )
    except Rol.DoesNotExist:
        return Response(
            {'error': 'Rol no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_permiso(request, id):
    try:
        permiso = Permiso.objects.get(id=id)
        permiso.delete()
        return Response(
            {'mensaje': 'Permiso eliminado correctamente.'},
            status=status.HTTP_200_OK
        )
    except Permiso.DoesNotExist:
        return Response(
            {'error': 'Permiso no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_tecnicos(request):
    tecnicos = Tecnico.objects.all()
    serializer = TecnicoSerializer(tecnicos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# (Asegúrate de importar tu modelo y serializer de Tecnico)

# ... (tu vista 'listar_tecnicos' va aquí) ...

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tecnico_por_id(request, id):
    try:
        # 1. Busca el técnico por su ID
        tecnico = Tecnico.objects.get(id=id)
    except Tecnico.DoesNotExist:
        # 2. Si no lo encuentra, devuelve el error 404 que tu frontend espera
        return Response({'error': 'Técnico no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    # 3. Si lo encuentra, lo serializa y lo devuelve
    serializer = TecnicoSerializer(tecnico)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_mi_perfil(request):
    """
    Devuelve la información del usuario (cliente) que está autenticado
    basado en el token enviado.
    """
    usuario = request.user
    try:
        serializer = UsuarioSerializers(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Ocurrió un error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_mi_perfil(request):
    """
    Actualiza la información del perfil del usuario autenticado.
    """
    usuario = request.user
    serializer = UsuarioSerializers(usuario, data=request.data, partial=True, 
                                    fields=['nombre', 'telefono', 'direccion', 'url_img'])

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







