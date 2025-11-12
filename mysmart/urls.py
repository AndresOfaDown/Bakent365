from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def index(request):
    return JsonResponse({"mensaje": "Backend Django desplegado correctamente"})

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),

    path('api/', include('productos.urls')),  
    path('api/', include('usuarios.urls')),
    path('api/', include('reportes.urls')), 
    path('api/', include('ventas.urls')),
    path('api/ia/', include('prediccion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
