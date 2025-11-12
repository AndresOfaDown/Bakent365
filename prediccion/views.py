from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# ¡¡IMPORTANTE!!
# Asumo que estos archivos (train_model.py y predict_model.py)
# los copiarás también dentro de la carpeta 'prediccion/'
from .train_model import entrenar_modelo
from .predict_model import generar_predicciones
from .models import PrediccionVenta


@api_view(['POST'])
def entrenar(request):
    resultado = entrenar_modelo()
    return Response({
        "mensaje": "Modelo entrenado correctamente",
        "mse": resultado["mse"],
        "r2": resultado["r2"]
    })

@api_view(['POST'])
def predecir(request):
    resultados = generar_predicciones()
    return Response({
        "mensaje": "Predicciones generadas correctamente",
        "resultados": resultados
    })

@api_view(['GET'])
def dashboard(request):
    predicciones = PrediccionVenta.objects.values('periodo', 'valor_predicho')
    return Response(list(predicciones))