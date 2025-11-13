"# 🏢 Bakent365 - Backend API

Sistema backend para SmartSales365 - Plataforma de gestión de ventas e inventario con inteligencia artificial y pagos con Stripe.

## 🚀 Características

- ✅ API REST con Django REST Framework
- ✅ Autenticación JWT
- ✅ Gestión de usuarios, productos, ventas y reportes
- ✅ Integración con Stripe para pagos
- ✅ Predicción con Machine Learning
- ✅ Generación de reportes en PDF y Excel
- ✅ Base de datos PostgreSQL
- ✅ Configurado para Docker y Railway

## 📋 Requisitos

- Python 3.13+
- PostgreSQL
- pip

## 🛠️ Instalación Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/AndresOfaDown/smar365.git
cd Backend/Bakent365
```

### 2. Crear entorno virtual
```bash
python -m venv env
# Windows
.\env\Scripts\activate
# Linux/Mac
source env/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Ejecutar migraciones
```bash
python manage.py migrate
```

### 6. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 7. Ejecutar servidor
```bash
python manage.py runserver
```

El servidor estará disponible en `http://localhost:8000`

## 🐳 Docker

### Desarrollo con Docker Compose
```bash
# Construir y ejecutar
docker-compose up --build

# Solo ejecutar (si ya está construido)
docker-compose up

# Detener
docker-compose down
```

### Docker solo (sin compose)
```bash
# Construir imagen
docker build -t bakent365 .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -e SECRET_KEY=tu-secret-key \
  -e DEBUG=True \
  -e DATABASE_URL=postgresql://... \
  bakent365
```

## ☁️ Despliegue en Railway

Ver guía completa en [DEPLOY.md](./DEPLOY.md)

### Pasos rápidos:
1. Crear cuenta en [Railway.app](https://railway.app)
2. Crear nuevo proyecto desde GitHub
3. Agregar PostgreSQL database
4. Configurar variables de entorno
5. Railway desplegará automáticamente

## 📁 Estructura del Proyecto

```
Backend/Bakent365/
├── mysmart/              # Configuración principal
├── usuarios/             # App de usuarios y autenticación
├── productos/            # App de productos
├── ventas/              # App de ventas y carrito
│   └── stripe_service.py # Integración con Stripe
├── reportes/            # App de reportes
├── prediccion/          # App de predicción con ML
├── Dockerfile           # Configuración de Docker
├── docker-compose.yml   # Orquestación de contenedores
├── railway.json         # Configuración de Railway
├── requirements.txt     # Dependencias Python
└── .env                 # Variables de entorno (no versionar)
```

## 🔑 Variables de Entorno

Crear archivo `.env` con:

```bash
# Django
SECRET_KEY=tu-secret-key-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@host:port/database
# O configuración individual:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=5432

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🔐 API Endpoints

### Autenticación
- `POST /api/auth/login/` - Login con email y password
- `POST /api/auth/register/` - Registro de nuevo usuario
- `POST /api/auth/refresh/` - Refrescar token JWT

### Productos
- `GET /api/productos/` - Listar productos
- `GET /api/catalogo/` - Catálogo público
- `POST /api/productos/` - Crear producto (Admin)

### Ventas
- `GET /api/carrito/` - Ver carrito actual
- `POST /api/carrito/agregar/` - Agregar producto al carrito
- `POST /api/stripe/create-payment-intent/` - Crear intención de pago
- `POST /api/stripe/confirm-payment/` - Confirmar pago

### Reportes
- `GET /api/reportes/ventas/` - Reporte de ventas
- `GET /api/reportes/productos/` - Reporte de productos
- `GET /api/reportes/pdf/` - Generar PDF

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Con coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📊 Base de Datos

El proyecto usa PostgreSQL. Configuración en `settings.py`.

### Migraciones
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations
```

## 💳 Stripe Integration

Configurado para pagos con tarjeta de crédito.

**Tarjetas de prueba:**
- Número: `4242 4242 4242 4242`
- Fecha: Cualquier fecha futura
- CVC: Cualquier 3 dígitos

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto es privado y confidencial.

## 👥 Autores

- AndresOfaDown

## 🔗 Enlaces

- [Frontend Repository](https://github.com/AndresOfaDown/smar365)
- [Railway Docs](https://docs.railway.app/)
- [Django Docs](https://docs.djangoproject.com/)
- [Stripe Docs](https://stripe.com/docs)
" 
