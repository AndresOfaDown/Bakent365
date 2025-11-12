from rest_framework import serializers
from .models import Rol, Permiso, RolPermiso, Usuario, Bitacora, Administrador, Cliente, Notificacion, Tecnico
from django.contrib.auth.hashers import make_password

class UsuarioSerializers(serializers.ModelSerializer):
    rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all())
    rol_nombre = serializers.SerializerMethodField()
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 
            'nombre',
            'email', 
            'password', 
            'telefono', 
            'direccion', 
            'url_img', 
            'estado', 
            'rol', 
            'rol_nombre'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    # El método debe estar dentro de la clase
    def get_rol_nombre(self, obj):
        return obj.rol.nombre if obj.rol else None

    # Validar email duplicado
    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está registrado.")
        return value

    # Crear usuario con contraseña encriptada y rol asignado
    def create(self, validated_data):
        usuario = Usuario.objects.create(
            nombre=validated_data['nombre'],
            email=validated_data['email'],
            telefono=validated_data.get('telefono'),
            direccion=validated_data.get('direccion'),
            rol=validated_data.get('rol'),
            password=make_password(validated_data['password']),
        )

        rol_id = validated_data.get('rol').id
        if rol_id == 1:  # Administrador
            Administrador.objects.create(administrador=usuario)
        elif rol_id == 2:  # Cliente
            Cliente.objects.create(cliente=usuario)
        elif rol_id == 3:  # Técnico
            # Creamos el perfil Técnico vinculado a este usuario
            Tecnico.objects.create(
                nombre=usuario.nombre,  # toma el nombre del usuario
                ci=f"CI-{usuario.id}",  # puedes reemplazar por otro campo si lo manejas en el registro
                telefono=usuario.telefono,
                area="Sin área definida",
                usuario=usuario
            )
        return usuario


class UsuarioAdminUpdateSerializers(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = ['id', 
                  'nombre',
                  'email', 
                  'telefono', 
                  'direccion', 
                  'url_img', 
                  'estado', 
                  'rol'
                  ]
        
class BitacoraSerializers(serializers.ModelSerializer):
    # 🔹 Campos derivados del usuario relacionado
    usuario_id = serializers.IntegerField(source='usuario.id', read_only=True)
    nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    correo = serializers.EmailField(source='usuario.email', read_only=True)
    rol = serializers.CharField(source='usuario.rol.nombre', read_only=True)
    ip = serializers.CharField(source='dir_ip', read_only=True)
    fecha = serializers.SerializerMethodField()

    class Meta:
        model = Bitacora
        fields = ['id', 'accion', 'fecha', 'ip', 'usuario_id', 'nombre', 'correo', 'rol']

    def get_fecha(self, obj):
        """
        Devuelve la fecha y hora formateada (ej: 2025-11-01 03:25:42)
        """
        if obj.fecha_hora:
            return obj.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        return "Fecha no válida"

        
class RolSerializers(serializers.ModelSerializer):
        class Meta:
            model = Rol
            fields = ['id', 'nombre']

class PermisoSerializers(serializers.ModelSerializer):
        class Meta:
            model = Permiso
            fields = ['id', 'nombre']
    
class NotificacionSerializers(serializers.ModelSerializer):
        class Meta:
            model = Notificacion
            fields = ['id', 
                      'titulo', 
                      'mensaje', 
                      'fecha_envio', 
                      'usuario'
                      ]

from .models import Tecnico

class TecnicoSerializer(serializers.ModelSerializer):
    usuario_id = serializers.IntegerField(source='usuario.id', read_only=True)
    usuario_email = serializers.EmailField(source='usuario.email', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)

    class Meta:
        model = Tecnico
        fields = [
            'id',
            'nombre',
            'ci',
            'telefono',
            'area',
            'usuario_id',
            'usuario_nombre',
            'usuario_email'
        ]





    