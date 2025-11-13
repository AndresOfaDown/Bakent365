from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from .stripe_service import crear_payment_intent, confirmar_pago  # ✅ Importar Stripe
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
    cantidad = request.data.get('cantidad', 1)  # ✅ Soportar cantidad
    
    if not producto_id:
        return Response({'error': 'Debe enviar el ID del producto'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    carrito, created = CarritoCompra.objects.get_or_create(cliente=cliente, estado='pendiente')
    
    # ✅ Verificar si el producto ya existe en el carrito
    detalle_existente = CarritoDetalle.objects.filter(carrito=carrito, producto=producto).first()
    
    if detalle_existente:
        # Si ya existe, NO crear duplicado - solo retornar éxito
        # (el frontend maneja la cantidad internamente)
        carrito.total = sum([item.producto.precio for item in carrito.detalles.all()])
        carrito.save()
        return Response({
            'mensaje': f'{producto.nombre} ya está en el carrito', 
            'total_actual': carrito.total,
            'detalle_id': detalle_existente.id
        }, status=status.HTTP_200_OK)
    else:
        # Crear nuevo detalle
        detalle = CarritoDetalle.objects.create(carrito=carrito, producto=producto)
        carrito.total = sum([item.producto.precio for item in carrito.detalles.all()])
        carrito.save()
        return Response({
            'mensaje': f'{producto.nombre} agregado correctamente', 
            'total_actual': carrito.total,
            'detalle_id': detalle.id
        }, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_cantidad_carrito(request, producto_id):
    """Actualizar cantidad de un producto en el carrito"""
    try:
        cliente = Cliente.objects.get(cliente=request.user)
    except Cliente.DoesNotExist:
        return Response({'error': 'El usuario no tiene un perfil de cliente.'}, status=status.HTTP_400_BAD_REQUEST)

    nueva_cantidad = request.data.get('cantidad')
    if nueva_cantidad is None or int(nueva_cantidad) < 0:
        return Response({'error': 'Cantidad inválida'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        carrito = CarritoCompra.objects.get(cliente=cliente, estado='pendiente')
    except CarritoCompra.DoesNotExist:
        return Response({'error': 'No hay un carrito pendiente.'}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Eliminar todos los detalles del producto
    CarritoDetalle.objects.filter(carrito=carrito, producto_id=producto_id).delete()
    
    # ✅ Agregar la nueva cantidad
    nueva_cantidad = int(nueva_cantidad)
    if nueva_cantidad > 0:
        try:
            producto = Producto.objects.get(id=producto_id)
            for _ in range(nueva_cantidad):
                CarritoDetalle.objects.create(carrito=carrito, producto=producto)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Recalcular total
    carrito.total = sum([item.producto.precio for item in carrito.detalles.all()])
    carrito.save()

    return Response({
        'mensaje': 'Cantidad actualizada correctamente',
        'total_actual': carrito.total
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def vaciar_carrito(request):
    """Vaciar todo el carrito"""
    try:
        cliente = Cliente.objects.get(cliente=request.user)
    except Cliente.DoesNotExist:
        return Response({'error': 'El usuario no tiene un perfil de cliente.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        carrito = CarritoCompra.objects.get(cliente=cliente, estado='pendiente')
        carrito.detalles.all().delete()
        carrito.total = 0
        carrito.save()
        return Response({'mensaje': 'Carrito vaciado correctamente'}, status=status.HTTP_200_OK)
    except CarritoCompra.DoesNotExist:
        return Response({'mensaje': 'No hay carrito pendiente'}, status=status.HTTP_200_OK)


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


# ================= STRIPE PAYMENT INTEGRATION =================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_stripe_payment_intent(request):
    """
    Crea un PaymentIntent de Stripe para procesar el pago del carrito
    """
    try:
        cliente = Cliente.objects.get(cliente=request.user)
    except Cliente.DoesNotExist:
        print(f"❌ Usuario {request.user.email} no tiene perfil de cliente")
        return Response(
            {'error': 'Solo los clientes pueden realizar pagos. Debe iniciar sesión con una cuenta de cliente.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Obtener carrito pendiente
    try:
        carrito = CarritoCompra.objects.get(cliente=cliente, estado='pendiente')
    except CarritoCompra.DoesNotExist:
        print(f"❌ Cliente {cliente.id} no tiene carrito pendiente")
        return Response(
            {'error': 'No hay un carrito pendiente.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if carrito.total <= 0:
        print(f"❌ Carrito {carrito.id} tiene total = {carrito.total}")
        return Response(
            {'error': 'El carrito está vacío.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        print(f"✅ Creando PaymentIntent para ${carrito.total}")
        
        # Crear PaymentIntent en Stripe
        payment_data = crear_payment_intent(
            monto=float(carrito.total),
            moneda='usd',
            metadata={
                'cliente_id': cliente.id,
                'carrito_id': carrito.id,
                'usuario_email': request.user.email
            }
        )

        print(f"✅ PaymentIntent creado: {payment_data['payment_intent_id']}")
        
        return Response({
            'client_secret': payment_data['client_secret'],
            'payment_intent_id': payment_data['payment_intent_id'],
            'amount': carrito.total,
            'carrito_id': carrito.id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"❌ Error en crear_stripe_payment_intent: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error al crear PaymentIntent: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def confirmar_stripe_payment(request):
    """
    Confirma el pago de Stripe y crea la venta en la BD
    """
    try:
        cliente = Cliente.objects.get(cliente=request.user)
    except Cliente.DoesNotExist:
        return Response(
            {'error': 'El usuario no tiene un perfil de cliente.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    payment_intent_id = request.data.get('payment_intent_id')
    nit = request.data.get('nit', None)

    if not payment_intent_id:
        return Response(
            {'error': 'Debe proporcionar el payment_intent_id'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Verificar el pago en Stripe
        pago_info = confirmar_pago(payment_intent_id)

        if not pago_info['paid']:
            return Response(
                {'error': 'El pago no fue exitoso en Stripe.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener carrito
        carrito = CarritoCompra.objects.filter(
            cliente=cliente,
            estado='pendiente'
        ).first()

        if not carrito:
            return Response(
                {'error': 'No hay carrito pendiente.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear venta
        venta = Venta.objects.create(
            cliente=cliente,
            total=carrito.total
        )

        # Crear detalles de venta
        for item in carrito.detalles.all():
            DetalleVenta.objects.create(
                venta=venta,
                producto=item.producto,
                precio_unitario=item.producto.precio
            )

        # Registrar el pago con referencia de Stripe
        pago = Pago.objects.create(
            venta=venta,
            tipo='Stripe',
            monto=carrito.total,
            fecha_pago=timezone.now()
        )

        # Generar nota de venta
        nota = NotaVenta.objects.create(
            venta=venta,
            fecha=timezone.now(),
            nit=nit,
            monto=carrito.total
        )

        # Cambiar estado del carrito
        carrito.estado = 'pagado'
        carrito.save()

        return Response({
            'mensaje': '✅ Pago procesado exitosamente con Stripe',
            'payment_intent_id': payment_intent_id,
            'venta': {
                'id': venta.id,
                'total': float(venta.total)
            },
            'nota_venta': {
                'id': nota.id,
                'nit': nota.nit,
                'monto': float(nota.monto)
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': f'Error al confirmar pago: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
