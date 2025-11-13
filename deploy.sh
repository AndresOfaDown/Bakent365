#!/bin/bash

# Script para desplegar en Railway

echo "🚀 Preparando despliegue en Railway..."

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Este script debe ejecutarse desde el directorio Backend/Bakent365"
    exit 1
fi

# Verificar que los archivos necesarios existen
echo "📋 Verificando archivos necesarios..."
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Dockerfile no encontrado"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt no encontrado"
    exit 1
fi

if [ ! -f "railway.json" ]; then
    echo "❌ Error: railway.json no encontrado"
    exit 1
fi

echo "✅ Todos los archivos necesarios están presentes"

# Verificar que las dependencias están actualizadas
echo "📦 Verificando dependencias..."
grep -q "gunicorn" requirements.txt || echo "⚠️  Advertencia: gunicorn no encontrado en requirements.txt"
grep -q "python-decouple" requirements.txt || echo "⚠️  Advertencia: python-decouple no encontrado en requirements.txt"
grep -q "whitenoise" requirements.txt || echo "⚠️  Advertencia: whitenoise no encontrado en requirements.txt"

# Mostrar recordatorios
echo ""
echo "📝 Recordatorios para Railway:"
echo "1. Crear proyecto en Railway.app"
echo "2. Agregar PostgreSQL database"
echo "3. Configurar las siguientes variables de entorno:"
echo "   - SECRET_KEY (generar nueva para producción)"
echo "   - DEBUG=False"
echo "   - ALLOWED_HOSTS=.railway.app"
echo "   - STRIPE_SECRET_KEY"
echo "   - STRIPE_PUBLIC_KEY"
echo "   - CORS_ALLOWED_ORIGINS (incluir dominio del frontend)"
echo ""
echo "4. Railway detectará automáticamente:"
echo "   - DATABASE_URL (desde PostgreSQL)"
echo "   - PORT (asignado automáticamente)"
echo ""

# Preguntar si desea hacer commit
read -p "¿Deseas hacer commit y push a GitHub? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "📤 Agregando archivos al staging..."
    git add .
    
    read -p "Mensaje del commit: " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Configuración para despliegue en Railway"
    fi
    
    git commit -m "$commit_msg"
    
    echo "🚀 Haciendo push a GitHub..."
    git push origin main
    
    echo "✅ ¡Listo! Railway detectará los cambios y comenzará el despliegue"
else
    echo "ℹ️  No se hicieron cambios en el repositorio"
    echo "   Ejecuta manualmente: git add . && git commit -m 'Deploy config' && git push"
fi

echo ""
echo "🎉 ¡Configuración completa!"
echo "   Visita https://railway.app para monitorear el despliegue"
