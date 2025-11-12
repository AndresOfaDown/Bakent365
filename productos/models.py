from django.db import models
from django.utils import timezone
# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'categoria'

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'marca'

class Descuento(models.Model):
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True, default=None)

    class Meta:
        db_table = 'descuento'

    def __str__(self):
        return f"{self.porcentaje}% - {self.descripcion or 'Descuento general'}"


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.URLField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='productos')
    descuento = models.ForeignKey(Descuento,on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')

    class Meta:
        db_table = 'producto'

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario')
    cantidad = models.IntegerField(default=0)

    class Meta: 
        db_table = 'inventario'

class Garantia(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='garantia')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        db_table = 'garantia'



