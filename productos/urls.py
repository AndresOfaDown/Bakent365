from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import listar_categorias, crear_categoria, eliminar_categoria, listar_productos, crear_producto,detalle_producto,actualizar_producto, eliminar_producto, crear_inventario,listar_catalogo,recomendar_productos_por_lista, crear_garantia, listar_marcas, crear_descuento, listar_descuentos,crear_marca, listar_garantias, listar_inventario,actualizar_inventario, asignar_descuento, listar_productos_con_descuento, listar_productos_sin_garantia

urlpatterns = [
    #categorias
    path('categorias/', listar_categorias ),
    path('categorias/crear/', crear_categoria),
    path('categoria/eliminar/<int:id>/', eliminar_categoria),
    #productos
    path('productos/', listar_productos),
    path('productos/crear/', crear_producto),
    path('productos/<int:id>/', detalle_producto),
    path('productos/actualizar/<int:id>/', actualizar_producto),
    path('productos/eliminar/<int:id>/', eliminar_producto),        
    path('productos/con-descuento/', listar_productos_con_descuento),


    path('catalogo/', listar_catalogo),
    path('recomendaciones/', recomendar_productos_por_lista),

    path('marcas/crear/', crear_marca),
    path('marcas/', listar_marcas),

    path('descuentos/crear/', crear_descuento),
    path('descuentos/', listar_descuentos),
    path('descuentos/asignar-descuento/<int:id>/', asignar_descuento),

    #garantias
    path('garantias/crear/', crear_garantia),
    path('garantias/', listar_garantias),
    path('productos/sin-garantia/', listar_productos_sin_garantia),

    #Inventario
    path('inventario/crear/', crear_inventario),
    path('inventario/', listar_inventario),
    path('inventario/actualizar/<int:id>/',actualizar_inventario),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)