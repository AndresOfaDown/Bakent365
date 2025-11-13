# 🚀 Guía de Despliegue en Railway

## 📋 Requisitos Previos
- Cuenta en [Railway.app](https://railway.app)
- Git instalado
- Repositorio en GitHub

## 🛠️ Configuración de Railway

### 1. Crear un Nuevo Proyecto en Railway

1. Ingresa a [Railway.app](https://railway.app)
2. Click en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu repositorio `smar365`

### 2. Configurar Base de Datos PostgreSQL

1. En tu proyecto de Railway, click en "+ New"
2. Selecciona "Database" → "PostgreSQL"
3. Railway creará automáticamente la base de datos
4. Copia la URL de conexión (DATABASE_URL)

### 3. Configurar Variables de Entorno

En la configuración de tu servicio Django, añade las siguientes variables:

```bash
# Django Settings
SECRET_KEY=tu-secret-key-segura-aqui
DEBUG=False
ALLOWED_HOSTS=.railway.app

# Database (automáticamente proporcionada por Railway)
DATABASE_URL=postgresql://...

# Stripe
STRIPE_SECRET_KEY=sk_test_51SOpP3D9rf9HDuNtlFTbuMSNpxtCON5rsRaXSwW4OcUOgpMs07YVesOBj7H95R9STFVtUWweMd1TW5cFOt1f6i8B00MOUL08zX
STRIPE_PUBLIC_KEY=pk_test_51SOpP3D9rf9HDuNt9TsnKuj0utwp2knkDjBsK4yTzYiUiPgDVPXLul7OjzJo4Ay7Qeh8p47bFsOJiDsAJPay4X9d00b6hzbYm7

# CORS - Agrega tu dominio de frontend
CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app,http://localhost:5173

# Puerto (Railway lo proporciona automáticamente)
PORT=8000
```

### 4. Configurar el Build

Railway detectará automáticamente el `Dockerfile` y lo usará para construir la aplicación.

Si necesitas configuración personalizada, el archivo `railway.json` ya está configurado.

### 5. Desplegar

1. Haz push de tus cambios a GitHub:
```bash
cd Backend/Bakent365
git add .
git commit -m "Configuración para Railway"
git push origin main
```

2. Railway detectará los cambios y comenzará el despliegue automáticamente

### 6. Verificar el Despliegue

1. En Railway, ve a la pestaña "Deployments"
2. Revisa los logs para asegurarte de que no hay errores
3. Una vez completado, Railway te dará una URL pública

## 🔧 Comandos Útiles

### Ver logs en Railway
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Ver logs
railway logs
```

### Ejecutar migraciones manualmente (si es necesario)
```bash
railway run python manage.py migrate
```

### Crear superusuario en producción
```bash
railway run python manage.py createsuperuser
```

## 📝 Notas Importantes

1. **SECRET_KEY**: Genera una nueva SECRET_KEY para producción:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

2. **DEBUG**: Asegúrate de que `DEBUG=False` en producción

3. **ALLOWED_HOSTS**: Agrega tu dominio de Railway (.railway.app)

4. **CORS**: Agrega el dominio de tu frontend en `CORS_ALLOWED_ORIGINS`

5. **Archivos estáticos**: WhiteNoise ya está configurado para servir archivos estáticos

6. **Base de datos**: Railway proporciona automáticamente la variable `DATABASE_URL`

## 🐳 Despliegue con Docker Local

Para probar el Dockerfile localmente:

```bash
# Construir la imagen
docker build -t bakent365 .

# Ejecutar el contenedor
docker run -p 8000:8000 \
  -e SECRET_KEY=tu-secret-key \
  -e DEBUG=True \
  -e DATABASE_URL=postgresql://... \
  bakent365
```

## 🔄 Actualizar Despliegue

Cada vez que hagas push a la rama `main`, Railway desplegará automáticamente los cambios.

## 🚨 Troubleshooting

### Error: No module named 'decouple'
```bash
# Asegúrate de que requirements.txt incluye:
python-decouple==3.8
```

### Error: ALLOWED_HOSTS
```bash
# Agrega el dominio de Railway en variables de entorno:
ALLOWED_HOSTS=.railway.app,tu-dominio.railway.app
```

### Error de base de datos
```bash
# Verifica que DATABASE_URL esté configurada
# Railway la proporciona automáticamente si agregaste PostgreSQL
```

## 📊 Monitoreo

Railway proporciona:
- Métricas de CPU y memoria
- Logs en tiempo real
- Historial de despliegues
- Alertas automáticas

## 💰 Costos

Railway ofrece:
- $5 USD gratis mensualmente
- Pago por uso después del crédito gratuito
- Estimación de costos en el dashboard

## 🔗 Enlaces Útiles

- [Documentación de Railway](https://docs.railway.app/)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Django en Railway](https://docs.railway.app/guides/django)
