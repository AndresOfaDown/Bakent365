import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from django.db import connection
from .models import ModeloPrediccion

def entrenar_modelo():
    df = pd.read_sql("SELECT id, total, fecha FROM venta", connection)
    df['mes'] = pd.to_datetime(df['fecha']).dt.month
    df['anio'] = pd.to_datetime(df['fecha']).dt.year

    X = df[['mes', 'anio']]
    y = df['total']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    joblib.dump(modelo, 'modelo_ventas.pkl')

    ModeloPrediccion.objects.create(r2_score=r2, mse=mse)
    return {"mse": mse, "r2": r2}
