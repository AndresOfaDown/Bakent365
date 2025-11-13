# Usar imagen de Python 3.13
FROM python:3.13-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    postgresql-client \
    libpq-dev \
    python3-dev \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    portaudio19-dev \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Añadir stripe si no está en requirements
RUN pip install stripe

# Copiar el proyecto
COPY . /app/

# Crear directorio para archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/media

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar las migraciones y luego el servidor
CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn mysmart.wsgi:application --bind 0.0.0.0:8000 --workers 3
