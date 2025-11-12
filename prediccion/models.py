from django.db import models

# Pega tus modelos aquí
class ModeloPrediccion(models.Model):
    nombre_modelo = models.CharField(max_length=100, default="Random Forest Regressor")
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True)
    r2_score = models.FloatField(null=True, blank=True)
    mse = models.FloatField(null=True, blank=True)
    version = models.CharField(max_length=20, default="1.0")

    class Meta:
        db_table = 'modelo_prediccion'

class PrediccionVenta(models.Model):
    modelo = models.ForeignKey(ModeloPrediccion, on_delete=models.CASCADE, related_name="predicciones")
    periodo = models.CharField(max_length=20)  # ejemplo: "2025-12"
    categoria = models.CharField(max_length=100, null=True, blank=True)
    valor_predicho = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_prediccion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prediccion_venta'