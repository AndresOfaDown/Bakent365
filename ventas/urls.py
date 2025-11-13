from django.urls import path
from .views import (
    ver_carrito, agregar_producto_carrito, eliminar_producto_carrito,
    actualizar_cantidad_carrito, vaciar_carrito,
    crear_pago, nota_venta_por_cliente, nota_venta_detalle, nota_venta_pdf,
    historial_compras_por_cliente,
    crear_stripe_payment_intent, confirmar_stripe_payment  # ✅ Stripe
)

urlpatterns = [
    path('carrito/', ver_carrito),
    path('carrito/agregar/', agregar_producto_carrito),
    path('carrito/actualizar/<int:producto_id>/', actualizar_cantidad_carrito),
    path('carrito/eliminar/<int:producto_id>/', eliminar_producto_carrito),
    path('carrito/vaciar/', vaciar_carrito),

    # Ventas
    path('pago/crear/', crear_pago),
    path('notas/', nota_venta_por_cliente),
    path('notas/<int:id>/', nota_venta_detalle),
    path('notas/<int:id>/pdf/', nota_venta_pdf),
    path('historial/<int:cliente_id>/', historial_compras_por_cliente),

    # Stripe Payments
    path('stripe/create-payment-intent/', crear_stripe_payment_intent),
    path('stripe/confirm-payment/', confirmar_stripe_payment),
]
