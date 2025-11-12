from rest_framework import serializers
from .models import Categoria, Marca, Producto, Inventario, Descuento, Garantia

class CategoriaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['id', 'nombre']


class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = ['id', 'porcentaje', 'descripcion', 'fecha_inicio', 'fecha_fin']

class GarantiaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = Garantia
        fields = ['id', 'producto', 'producto_nombre', 'fecha_inicio', 'fecha_fin']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    descuento_porcentaje = serializers.DecimalField(source='descuento.porcentaje', read_only=True, max_digits=5, decimal_places=2)
    descuento = DescuentoSerializer(read_only=True)
    descuento_id = serializers.PrimaryKeyRelatedField(
        queryset=Descuento.objects.all(), source='descuento', write_only=True, required=False
    )
    precio_final = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    garantia = GarantiaSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 'precio_final', 'imagen', 'estado',
            'categoria', 'categoria_nombre', 'marca', 'marca_nombre',
            'descuento', 'descuento_porcentaje', 'descuento_id', 'garantia'
        ]




class InventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = Inventario
        fields = ['id', 'producto', 'producto_nombre', 'cantidad']


