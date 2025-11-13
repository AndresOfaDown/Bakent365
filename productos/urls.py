from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import (
    listar_categorias, crear_categoria, eliminar_categoria,
    listar_productos, crear_producto, detalle_producto,
    actualizar_producto, eliminar_producto,
    crear_inventario, listar_catalogo, recomendar_productos_por_lista,
    crear_garantia, listar_garantias, eliminar_garantia, actualizar_garantia,
    listar_marcas, crear_marca, eliminar_marca,
    crear_descuento, listar_descuentos, eliminar_descuento,
    actualizar_descuento, asignar_descuento,
    listar_inventario, actualizar_inventario,
    listar_productos_con_descuento, listar_productos_sin_garantia
)

urlpatterns = [
    # Categorias
    path('categorias/', listar_categorias),
    path('categorias/crear/', crear_categoria),
    path('categoria/eliminar/<int:id>/', eliminar_categoria),
    
    # Productos
    path('productos/', listar_productos),
    path('productos/crear/', crear_producto),
    path('productos/<int:id>/', detalle_producto),
    path('productos/actualizar/<int:id>/', actualizar_producto),
    path('productos/eliminar/<int:id>/', eliminar_producto),
    path('productos/con-descuento/', listar_productos_con_descuento),
    path('productos/sin-garantia/', listar_productos_sin_garantia),

    # Catalogo y recomendaciones
    path('catalogo/', listar_catalogo),
    path('recomendaciones/', recomendar_productos_por_lista),

    # Marcas
    path('marcas/', listar_marcas),
    path('marcas/crear/', crear_marca),
    path('marcas/eliminar/<int:id>/', eliminar_marca),

    # Descuentos
    path('descuentos/', listar_descuentos),
    path('descuentos/crear/', crear_descuento),
    path('descuentos/<int:id>/', actualizar_descuento),
    path('descuentos/eliminar/<int:id>/', eliminar_descuento),
    path('descuentos/asignar-descuento/<int:id>/', asignar_descuento),

    # Garantias
    path('garantias/', listar_garantias),
    path('garantias/crear/', crear_garantia),
    path('garantias/<int:id>/', actualizar_garantia),
    path('garantias/eliminar/<int:id>/', eliminar_garantia),

    # Inventario
    path('inventario/', listar_inventario),
    path('inventario/crear/', crear_inventario),
    path('inventario/actualizar/<int:id>/', actualizar_inventario),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
