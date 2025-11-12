# El comando startapp no crea este archivo,
# así que créalo tú mismo: 'prediccion/urls.py'

from django.urls import path
from .views import entrenar, predecir, dashboard

urlpatterns = [
    path('entrenar/', entrenar),
    path('predecir/', predecir),
    path('dashboard/', dashboard),
]