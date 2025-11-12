from django.db import models
from usuarios.models import Usuario

class Reporte(models.Model):
    tipo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey("usuarios.Usuario", on_delete=models.CASCADE, related_name='reportes')

    class Meta:
        db_table = 'reporte'
 
    def __str__(self):
        return f'{self.tipo} - {self.fecha.strftime("%d/%m/%Y")}'


class Mantenimiento(models.Model):
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.TextField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tecnico = models.ForeignKey(
        "usuarios.Tecnico",
        on_delete=models.SET_NULL,     # si se elimina el técnico, queda null
        null=True,                     # permite valor nulo
        blank=True,                    # permite dejar vacío en formularios
        related_name='mantenimientos'
    )
    cliente = models.ForeignKey("usuarios.Usuario", on_delete=models.CASCADE,null=True, blank=True,related_name='mantenimientos_cliente')
    estado = models.CharField(max_length=20, default='pendiente')

    class Meta:
        db_table = 'mantenimiento'

    def __str__(self):
        return f"Mantenimiento #{self.id} - Cliente: {self.cliente.nombre}"
    




