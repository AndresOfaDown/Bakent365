from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import CarritoCompra, CarritoDetalle, Pago, Venta, DetalleVenta, NotaVenta
from .serializers import CarritoCompraSerializer, NotaVentaSerializer
from productos.models import Producto
from usuarios.models import Cliente, Usuario
from django.utils import timezone
import uuid
from django.db import transaction
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
#@transaction.atomic


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_carrito(request):
    try:
        # ✅ Obtener el cliente asociado al usuario autenticado
        cliente = Cliente.objects.get(cliente=request.user)
    except Cliente.DoesNotExist:
        return Response({'error': 'El usuario no tiene un perfil de cliente.'}, status=status.HTTP_400_BAD_REQUEST)

    carrito, created = CarritoCompra.objects.get_or_create(cliente=cliente, estado='pendiente')

    serializer = CarritoCompraSerializer(carrito)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_producto_carrito(request):
    try:
        cliente = Cliente.objects.get(cliente=request.user)
    except Cliente.DoesNotExist:
        return Response({'error': 'El usuario no es un cliente registrado.'}, status=status.HTTP_400_BAD_REQUEST)

    producto_id = request.data.get('producto_id')
    if not producto_id:
        return Response({'error': 'Debe enviar el ID del producto'}, status=status.HTTP_400_BAD_REQUEST)

    carrito, created = CarritoCompra.objects.get_or_create(cliente=cliente, estado='pendiente')
    producto = Producto.objects.get(id=producto_id)
    detalle, created = CarritoDetalle.objects.get_or_create(carrito=carrito, producto=producto)

    carrito.total = sum([item.producto.precio for item in carrito.detalles.all()])
    carrito.save()

    return Response({'mensaje': 'Producto agregado correctamente', 'total_actual': carrito.total}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_producto_carrito(request, producto_id):
    try:
        # ✅ Buscar perfil Cliente del usuario autenticado
        cliente = Cliente.objects.get(cliente=request.user)
    except Cliente.DoesNotExist:
        return Response(
            {'error': 'El usuario autenticado no tiene un perfil de cliente.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # ✅ Buscar el carrito del cliente
        carrito = CarritoCompra.objects.get(cliente=cliente, estado='pendiente')
    except CarritoCompra.DoesNotExist:
        return Response({'error': 'No hay un carrito pendiente.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # ✅ Buscar el detalle del producto dentro del carrito
        detalle = CarritoDetalle.objects.get(carrito=carrito, producto_id=producto_id)
        detalle.delete()

        # ✅ Recalcular el total del carrito
        carrito.total = sum([item.producto.precio for item in carrito.detalles.all()])
        carrito.save()

        return Response({'mensaje': 'Producto eliminado del carrito correctamente.'}, status=status.HTTP_200_OK)

    except CarritoDetalle.DoesNotExist:
        return Response({'error': 'El producto no se encuentra en el carrito.'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def crear_pago(request):
    """
    Simulación de pago online (Stripe / PayPal).
    Crea Venta, Detalles, Pago y Nota de Venta con transacción atómica.
    """
    try:
        cliente = Cliente.objects.get(cliente=request.user)
    except Cliente.DoesNotExist:
        return Response({'error': 'El usuario autenticado no tiene perfil de cliente.'},
                        status=status.HTTP_400_BAD_REQUEST)

    tipo_pago = request.data.get('tipo')  # Ej: 'stripe', 'paypal', 'efectivo'
    nit = request.data.get('nit', None)

    # 1️⃣ Obtener carrito pendiente
    carrito = CarritoCompra.objects.filter(cliente=cliente, estado='pendiente').first()
    if not carrito:
        return Response({'error': 'No hay un carrito pendiente para procesar.'},
                        status=status.HTTP_404_NOT_FOUND)

    if carrito.total <= 0:
        return Response({'error': 'El carrito está vacío.'}, status=status.HTTP_400_BAD_REQUEST)

    # 2️⃣ Crear venta
    venta = Venta.objects.create(cliente=cliente, total=carrito.total)

    # 3️⃣ Crear detalles de venta con precios históricos
    for item in carrito.detalles.all():
        DetalleVenta.objects.create(
            venta=venta,
            producto=item.producto,
            precio_unitario=item.producto.precio
        )

    # 4️⃣ Simular pago (Stripe / PayPal)
    if tipo_pago.lower() == 'stripe':
        # token simulado de Stripe
        referencia_pago = f"STRIPE-{uuid.uuid4().hex[:10].upper()}"
    elif tipo_pago.lower() == 'paypal':
        referencia_pago = f"PAYPAL-{uuid.uuid4().hex[:10].upper()}"
    else:
        referencia_pago = f"LOCAL-{uuid.uuid4().hex[:10].upper()}"

    # 5️⃣ Registrar el pago
    pago = Pago.objects.create(
        venta=venta,
        tipo=tipo_pago.capitalize(),
        monto=carrito.total,
        fecha_pago=timezone.now()
    )

    # 6️⃣ Generar nota de venta
    nota = NotaVenta.objects.create(
        venta=venta,
        fecha=timezone.now(),
        nit=nit,
        monto=carrito.total
    )

    # 7️⃣ Cambiar estado del carrito
    carrito.estado = 'pagado'
    carrito.save()

    return Response({
        'mensaje': '✅ Pago procesado exitosamente (simulado).',
        'referencia': referencia_pago,
        'venta': {
            'id': venta.id,
            'total': float(carrito.total),
            'tipo_pago': tipo_pago.capitalize()
        },
        'nota_venta': {
            'id': nota.id,
            'nit': nota.nit,
            'monto': float(nota.monto),
            'fecha': nota.fecha.strftime("%Y-%m-%d %H:%M:%S")
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nota_venta_por_cliente(request):

    #listar notaa de venta del cliente autenticado
    try:
        cliente = Cliente.objects.get(cliente=request.user)
    except Cliente.DoesNotExist:
        return Response({'error': 'El usuario no tiene un perfil de cliente.'}, status=status.HTTP_400_BAD_REQUEST)
    
    notas = NotaVenta.objects.filter(venta__cliente=cliente).order_by('-fecha')
    serializer = NotaVentaSerializer(notas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nota_venta_detalle(request, id):
    """Ver el detalle completo de una nota de venta"""
    try:
        nota = NotaVenta.objects.get(id=id, venta__cliente__cliente=request.user)
    except NotaVenta.DoesNotExist:
        return Response({'error': 'Nota de venta no encontrada o no pertenece al usuario.'},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = NotaVentaSerializer(nota)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nota_venta_pdf(request, id):
    """Generar PDF de una nota de venta"""
    try:
        nota = NotaVenta.objects.get(id=id, venta__cliente__cliente=request.user)
    except NotaVenta.DoesNotExist:
        return Response({'error': 'Nota de venta no encontrada o no pertenece al usuario.'},
                        status=status.HTTP_404_NOT_FOUND)

    template = get_template('nota_venta.html')
    html = template.render({'nota': nota})

    # Crear el archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="nota_venta_{nota.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return Response({'error': 'Error al generar el PDF'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_compras_por_cliente(request, cliente_id):
    """
    📜 Permite al administrador consultar el historial de compras
    de un cliente específico por su ID de usuario.
    """
    try:
        # Verificar que el usuario sea un cliente
        cliente_usuario = Usuario.objects.get(id=cliente_id)
        cliente = Cliente.objects.get(cliente=cliente_usuario)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    except Cliente.DoesNotExist:
        return Response({'error': 'Este usuario no tiene perfil de cliente.'}, status=status.HTTP_400_BAD_REQUEST)

    notas = NotaVenta.objects.filter(venta__cliente=cliente).order_by('-fecha')
    serializer = NotaVentaSerializer(notas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
