from rest_framework import serializers
from usuarios.models import Tecnico
from .models import Mantenimiento, Reporte



class MantenimientoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    tecnico_nombre = serializers.CharField(source='tecnico.nombre', read_only=True)

    class Meta:
        model = Mantenimiento
        fields = [
            'id', 'fecha', 'descripcion', 'costo_total',
            'cliente', 'cliente_nombre',
            'tecnico', 'tecnico_nombre', 'estado'
        ]
        extra_kwargs = {
            'tecnico': {'required': False, 'allow_null': True}
        }

class ReporteSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)

    class Meta:
        model = Reporte
        fields = ['id', 'tipo', 'descripcion', 'fecha', 'usuario', 'usuario_nombre']