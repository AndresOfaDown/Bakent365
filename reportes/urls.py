from django.urls import path
from .views import listar_mantenimientos, crear_mantenimiento, AsignarTecnicoView, listar_mantenimientos_por_tecnico, actualizar_estado_mantenimiento, generar_reporte_dinamico

urlpatterns = [
    path('mantenimientos/', listar_mantenimientos),
    path('mantenimientos/crear/', crear_mantenimiento),
    path('mantenimientos/<int:id>/asignar-tecnico/', AsignarTecnicoView.as_view()),   
    #path('mantenimiento/tecnicos/<int:id>/', mantenimientos_por_tecnico),
    #path('mantenimiento/tecnicos/<int:id>/', mantenimientos_por_cliente),
    path('mantenimientos/por-tecnico/', listar_mantenimientos_por_tecnico),
    path('mantenimientos/<int:id>/actualizar-estado/',actualizar_estado_mantenimiento),

    #Reportes
    path('reportes/dinamico/', generar_reporte_dinamico),

]