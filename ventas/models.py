from django.db import models
from usuarios.models import  Cliente
from productos.models import Producto

class CarritoCompra(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='carritos')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, default='pendiente')  # pendiente, pagado, cancelado

    class Meta:
        db_table = 'carrito_compra'

    def __str__(self):
        return f'Carrito #{self.id} - Cliente: {self.cliente}'


class CarritoDetalle(models.Model):
    carrito = models.ForeignKey(CarritoCompra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    class Meta:
        db_table = 'carrito_detalle'
        unique_together = ('carrito', 'producto')


# ---------- VENTAS ----------
class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'venta'

    def __str__(self):
        return f'Venta #{self.id} - {self.cliente.cliente.nombre}'


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    precio_unitario = models.DecimalField (max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_venta'

        def __str__(self):
            return f"{self.producto.nombre} - {self.precio_unitario}"


# ---------- PAGO ----------
class Pago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)  # Efectivo, Tarjeta, PayPal, Stripe
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pago'

    def __str__(self):
        return f'Pago #{self.id} - {self.tipo}'


# ---------- NOTA DE VENTA / FACTURA ----------
class NotaVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='nota')
    fecha = models.DateTimeField(auto_now_add=True)
    nit = models.CharField(max_length=20, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'nota_venta'

