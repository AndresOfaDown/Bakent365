import pandas as pd
import joblib
from .models import ModeloPrediccion, PrediccionVenta

def generar_predicciones():
    # ✅ Cargar el modelo entrenado más reciente
    modelo_guardado = ModeloPrediccion.objects.last()
    modelo = joblib.load('modelo_ventas.pkl')

    # ✅ Crear dataset de meses futuros
    df_futuro = pd.DataFrame({
        'mes': [11, 12, 1, 2, 3],   # meses de prueba
        'anio': [2025, 2025, 2026, 2026, 2026]
    })

    # ✅ Hacer predicciones
    predicciones = modelo.predict(df_futuro)

    # ✅ Guardar cada predicción en la base de datos
    for i in range(len(predicciones)):
        PrediccionVenta.objects.create(
            modelo=modelo_guardado,
            periodo=f"{df_futuro.loc[i,'anio']}-{df_futuro.loc[i,'mes']:02d}",
            valor_predicho=predicciones[i]
        )

    # ✅ Devolver las predicciones generadas
    resultados = [
        {"periodo": f"{df_futuro.loc[i,'anio']}-{df_futuro.loc[i,'mes']:02d}", 
         "prediccion": float(predicciones[i])}
        for i in range(len(predicciones))
    ]
    return resultados
