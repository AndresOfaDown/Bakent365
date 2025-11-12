from rest_framework import serializers
from usuarios.models import Cliente
from productos.models import Producto
from .models import Venta,NotaVenta,DetalleVenta,CarritoCompra,CarritoDetalle,Pago


class ProductoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'descripcion']

class CarritoDetalleSerializer(serializers.ModelSerializer):
    producto = ProductoSimpleSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(queryset= Producto.objects.all(), source='producto', write_only=True)

    class Meta:
        model = CarritoDetalle
        fields = ['id', 'producto', 'producto_id']

class CarritoCompraSerializer(serializers.ModelSerializer):
    detalles = CarritoDetalleSerializer(many=True, read_only=True)

    class Meta:
        model = CarritoCompra
        fields = ['id', 'fecha', 'total', 'estado', 'detalles']

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id', 'tipo', 'monto', 'fecha_pago']


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = ['id', 'producto', 'producto_nombre', 'precio_unitario']

class NotaVentaSerializer(serializers.ModelSerializer):
    venta_id = serializers.IntegerField(source='venta.id', read_only=True)
    detalles = DetalleVentaSerializer(source='venta.detalles', many=True, read_only=True)
    
    class Meta:
        model = NotaVenta
        fields = ['id', 'venta_id', 'fecha', 'nit', 'monto', 'detalles']




