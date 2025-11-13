from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .models import Categoria, Producto, Inventario, Marca, Descuento, Garantia
from .serializers import ProductoSerializer,InventarioSerializer, DescuentoSerializer, GarantiaSerializer
from usuarios.views import registrar_bitacora
from usuarios.views import get_usuario_info_desde_token_manual
import random
from rest_framework.permissions import AllowAny
from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_categoria(request):
    nombre = request.data.get('nombre')
    if not nombre:
        return Response({'error': 'Este campo es requerido.'},status=status.HTTP_400_BAD_REQUEST)
    if Categoria.objects.filter(nombre=nombre).exists():
        return Response({'error': 'Ya esxiste una Categoria con ese nombre'},status=status.HTTP_400_BAD_REQUEST)
    
    categoria = Categoria.objects.create(nombre=nombre)
    return Response({'mensaje': 'Categoria creado correctamente.','categoria': {'id': categoria.id, 'nombre': categoria.nombre}}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_categorias(request):
    categoria = Categoria.objects.all().values('id','nombre')
    return Response(list(categoria),status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_categoria(request,id):
   try:
       categoria = Categoria.objects.get(id=id)
       categoria.delete()
       return Response({'mensaje': 'Categoria eliminada correctamente.'}, status=status.HTTP_200_OK)
   except Categoria.DoesNotExist:
       return Response({'error': 'Categoria no encontrada.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_producto(request):
    serializer = ProductoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_productos(request):
    productos = Producto.objects.filter(estado=1).order_by('id')
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def detalle_producto(request, id):
    try:
        producto = Producto.objects.get(id=id)
        
        # --- INICIO DE LA CORRECCIÓN ---
        # Acceso seguro al inventario
        stock = 0 # Valor por defecto si no hay inventario
        if hasattr(producto, 'inventario'): # Comprueba si la relación 'inventario' existe
            stock = producto.inventario.cantidad
        # --- FIN DE LA CORRECCIÓN ---

        # Estos también deberían ser seguros, aunque probablemente no sean nulos
        marca_nombre = producto.marca.nombre if producto.marca else "Sin Marca"
        categoria_nombre = producto.categoria.nombre if producto.categoria else "Sin Categoría"
        
        print(f"Producto: {producto.nombre}, Descripción: {producto.descripcion}, Stock: {stock}")

        return Response({
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': producto.precio,
            'marca': marca_nombre,      # Usamos la variable segura
            'categoria': categoria_nombre, # Usamos la variable segura
            'dir_img': producto.imagen, # Asumo que 'imagen' puede ser null o string
            'stock': stock              # Usamos la variable segura
        })
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error inesperado en detalle_producto: {str(e)}") # Es bueno imprimir el error
        return Response({'error': f'Error interno del servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_producto(request,id):
    try:
        producto = Producto.objects.get(id=id)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado'},status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductoSerializer(producto, data=request.data, partial=True)
    if serializer.is_valid():
        info = get_usuario_info_desde_token_manual(request)
        registrar_bitacora(request, 'actualizo producto',info)
        serializer.save()
        return Response({'mensaje': 'Producto actualizado correctamente', 'producto':serializer.data})
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE']) 
@permission_classes([IsAuthenticated])
def eliminar_producto(request, id):
    try:
        producto = Producto.objects.get(id=id)
        producto.estado = 0
        producto.save()
        return Response({'mensaje': 'Producto eliminado (estado = 0)'})
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado'},status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_inventario(request):
    inventario = Inventario.objects.select_related('producto').all()
    serializer = InventarioSerializer(inventario, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_inventario(request, id):
    try:
        inventario = Inventario.objects.get(id=id)
    except Inventario.DoesNotExist:
        return Response({'error': 'Inventario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = InventarioSerializer(inventario, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'mensaje': 'Inventario actualizado correctamente.', 'data': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_inventario(request):
    producto_id = request.data.get('producto')
    cantidad = request.data.get('cantidad')

    if not producto_id or not cantidad:
        return Response({'error': 'Los campos productos y cantidad son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_400_BAD_REQUEST )
    #verificar si hay inventario para ese producto
    inventario_existente = Inventario.objects.filter(producto=producto).filter()
    if inventario_existente:
     return Response({'error': 'Ya existe inventario para ese producto'}, status=status.HTTP_400_BAD_REQUEST)

    inventario = Inventario.objects.create(
    producto=producto,
    cantidad=cantidad
    )
    return Response({
        'mensaje': 'Inventario creado exitosamente',
        'inventario': {
            'id': inventario.id,
            'producto': inventario.producto.nombre,
            'cantidad': inventario.cantidad
        }
    }, status=201)

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_catalogo(request):
    productos = Producto.objects.filter(estado=1).order_by('id')
    data = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'precio': p.precio,
            'dir_img': p.imagen,
        } for p in productos
    ]
    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def recomendar_productos_por_lista(request):
    productos_ids = request.data.get('productos', [])
    todos = list(Producto.objects.filter(estado=1).exclude(id__in=productos_ids))
    recomendados = random.sample(todos, min(5, len(todos)))

    data = [{'id_producto': p.id} for p in recomendados]
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_imagen_producto(request, id):
    try:
        producto = Producto.objects.get(id=id)
        return Response({'url': producto.imagen})
    except Producto.DoesNotExist:
        return Response({'url': ''})
    
@api_view(['GET'])
def get_inventario_producto(request, id):
    try:
        producto = Producto.objects.get(id=id)
        inventario = Inventario.objects.filter(producto=producto).first()
        cantidad = inventario.cantidad if inventario else 0
        return Response({'cantidad': cantidad})
    except Producto.DoesNotExist:
        return Response({'cantidad': 0})

# ---------- MARCAS ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_marca(request):
    nombre = request.data.get('nombre')
    if not nombre:
        return Response({'error': 'El campo nombre es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

    if Marca.objects.filter(nombre__iexact=nombre).exists():
        return Response({'error': 'Ya existe una marca con ese nombre.'}, status=status.HTTP_400_BAD_REQUEST)

    marca = Marca.objects.create(nombre=nombre)
    return Response(
        {
            'mensaje': 'Marca creada correctamente.',
            'marca': {'id': marca.id, 'nombre': marca.nombre}
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_marcas(request):
    marcas = Marca.objects.all().values('id', 'nombre')
    return Response(list(marcas), status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_marca(request, id):
    try:
        marca = Marca.objects.get(id=id)
        marca.delete()
        return Response({'mensaje': 'Marca eliminada correctamente.'}, status=status.HTTP_200_OK)
    except Marca.DoesNotExist:
        return Response({'error': 'Marca no encontrada.'}, status=status.HTTP_404_NOT_FOUND)


# ---------- DESCUENTOS ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_descuento(request):
    serializer = DescuentoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'mensaje': 'Descuento creado correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_descuentos(request):
    descuentos = Descuento.objects.all()
    serializer = DescuentoSerializer(descuentos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def asignar_descuento(request, id):
    try:
        producto = Producto.objects.get(id=id)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    descuento_id = request.data.get('descuento_id')
    if not descuento_id:
        return Response({'error': 'Debe proporcionar el ID del descuento.'}, status=status.HTTP_400_BAD_REQUEST)

    producto.descuento_id = descuento_id
    producto.save()

    serializer = ProductoSerializer(producto)
    return Response({'mensaje': 'Descuento asignado correctamente.', 'producto': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])  # visible para todos
def listar_productos_con_descuento(request):
    hoy = timezone.now().date()
    productos = Producto.objects.filter(
        descuento__isnull=False,
        descuento__fecha_inicio__lte=hoy,
        descuento__fecha_fin__gte=hoy
    )

    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# (Asegúrate de importar esto al principio de tu archivo)
from django.db import IntegrityError

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_garantia(request):
    producto_id = request.data.get('producto')
    fecha_inicio = request.data.get('fecha_inicio')
    fecha_fin = request.data.get('fecha_fin')

    if not (producto_id and fecha_inicio and fecha_fin):
        return Response({'error': 'Los campos producto, fecha_inicio y fecha_fin son obligatorios.'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    # --- INICIO DE LA CORRECCIÓN ---
    # Envolvemos la creación en un try...except
    try:
        garantia = Garantia.objects.create(
            producto=producto,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
    except IntegrityError:
        # Esto ocurre si el producto ya tiene una garantía (restricción 'unique')
        return Response({'error': 'Este producto ya tiene una garantía asignada.'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    # --- FIN DE LA CORRECCIÓN ---

    return Response(
        {
            'mensaje': 'Garantía creada correctamente.',
            'garantia': {
                'id': garantia.id,
                'producto': producto.nombre, # Tu vista 'listar' usa el nombre, así que la respuesta de 'crear' también lo hará
                'fecha_inicio': garantia.fecha_inicio,
                'fecha_fin': garantia.fecha_fin
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_garantias(request):
    garantias = Garantia.objects.all().select_related('producto')
    data = [
        {
            'id': g.id,
            'producto': g.producto.nombre,
            'producto_id': g.producto.id,
            'fecha_inicio': g.fecha_inicio,
            'fecha_fin': g.fecha_fin
        } for g in garantias
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_garantia(request, id):
    try:
        garantia = Garantia.objects.get(id=id)
        garantia.delete()
        return Response(
            {'mensaje': 'Garantía eliminada correctamente.'},
            status=status.HTTP_200_OK
        )
    except Garantia.DoesNotExist:
        return Response(
            {'error': 'Garantía no encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_garantia(request, id):
    try:
        garantia = Garantia.objects.get(id=id)
    except Garantia.DoesNotExist:
        return Response(
            {'error': 'Garantía no encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = GarantiaSerializer(
        garantia,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'mensaje': 'Garantía actualizada correctamente.',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_descuento(request, id):
    try:
        descuento = Descuento.objects.get(id=id)
        descuento.delete()
        return Response(
            {'mensaje': 'Descuento eliminado correctamente.'},
            status=status.HTTP_200_OK
        )
    except Descuento.DoesNotExist:
        return Response(
            {'error': 'Descuento no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_descuento(request, id):
    try:
        descuento = Descuento.objects.get(id=id)
    except Descuento.DoesNotExist:
        return Response(
            {'error': 'Descuento no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = DescuentoSerializer(
        descuento,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'mensaje': 'Descuento actualizado correctamente.',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_productos_sin_garantia(request):
    productos = Producto.objects.filter(garantia__isnull=True)
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)





  




    