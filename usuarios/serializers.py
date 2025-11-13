from rest_framework import serializers
from .models import (
    Rol, Permiso, RolPermiso, Usuario, Bitacora,
    Administrador, Cliente, Notificacion, Tecnico
)
from django.contrib.auth.hashers import make_password


class UsuarioSerializers(serializers.ModelSerializer):
    rol = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        required=False  # Hacemos el rol opcional para que tome el valor por defecto
    )
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

    def get_rol_nombre(self, obj):
        return obj.rol.nombre if obj.rol else None

    def validate_email(self, value):
        # Permitir el mismo email si estamos actualizando el mismo usuario
        if self.instance and self.instance.email == value:
            return value
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está registrado.")
        return value

    def create(self, validated_data):
        # Si no se proporciona rol, asignar rol Cliente por defecto
        if 'rol' not in validated_data or validated_data['rol'] is None:
            try:
                rol_cliente = Rol.objects.get(nombre='Cliente')
                validated_data['rol'] = rol_cliente
            except Rol.DoesNotExist:
                # Si no existe el rol Cliente, intentar crear o usar el de ID 2
                rol_cliente, _ = Rol.objects.get_or_create(
                    id=2,
                    defaults={'nombre': 'Cliente'}
                )
                validated_data['rol'] = rol_cliente
        
        # Asegurar que estado sea 1 por defecto
        if 'estado' not in validated_data:
            validated_data['estado'] = 1

        usuario = Usuario.objects.create(
            nombre=validated_data['nombre'],
            email=validated_data['email'],
            telefono=validated_data.get('telefono'),
            direccion=validated_data.get('direccion'),
            rol=validated_data.get('rol'),
            estado=validated_data.get('estado', 1),
            password=make_password(validated_data['password']),
        )

        # Crear la relación según el rol
        rol_id = validated_data.get('rol').id
        if rol_id == 1:  # Administrador
            Administrador.objects.create(administrador=usuario)
        elif rol_id == 2:  # Cliente
            Cliente.objects.create(cliente=usuario)
        elif rol_id == 3:  # Técnico
            Tecnico.objects.create(
                nombre=usuario.nombre,
                ci=f"CI-{usuario.id}",
                telefono=usuario.telefono,
                area="Sin área definida",
                usuario=usuario
            )
        return usuario


class UsuarioAdminUpdateSerializers(serializers.ModelSerializer):
    rol = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'id',
            'nombre',
            'email',
            'telefono',
            'direccion',
            'url_img',
            'estado',
            'rol'
        ]

    def validate_email(self, value):
        # Permitir el mismo email si estamos actualizando el mismo usuario
        if self.instance and self.instance.email == value:
            return value
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está registrado.")
        return value


class BitacoraSerializers(serializers.ModelSerializer):
    usuario_id = serializers.IntegerField(
        source='usuario.id',
        read_only=True
    )
    nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    correo = serializers.EmailField(source='usuario.email', read_only=True)
    rol = serializers.CharField(source='usuario.rol.nombre', read_only=True)
    ip = serializers.CharField(source='dir_ip', read_only=True)
    fecha = serializers.SerializerMethodField()

    class Meta:
        model = Bitacora
        fields = [
            'id', 'accion', 'fecha', 'ip',
            'usuario_id', 'nombre', 'correo', 'rol'
        ]

    def get_fecha(self, obj):
        """Devuelve la fecha y hora formateada"""
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
        fields = ['id', 'titulo', 'mensaje', 'fecha_envio', 'usuario']


class TecnicoSerializer(serializers.ModelSerializer):
    usuario_id = serializers.IntegerField(
        source='usuario.id',
        read_only=True
    )
    usuario_email = serializers.EmailField(
        source='usuario.email',
        read_only=True
    )
    usuario_nombre = serializers.CharField(
        source='usuario.nombre',
        read_only=True
    )

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





    