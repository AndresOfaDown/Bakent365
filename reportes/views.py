from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Mantenimiento, Reporte
from .serializers import MantenimientoSerializer, ReporteSerializer
from usuarios.models import Tecnico
from rest_framework.views import APIView
from ventas.models import Venta
import io, re, tempfile
from datetime import datetime
import speech_recognition as sr
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from pydub import AudioSegment
from pydub.utils import which
AudioSegment.converter = which("ffmpeg")
import pandas as pd
from .utils.generar_pdf import generar_pdf
from .utils.generar_excel import generar_excel
from django.http import FileResponse, JsonResponse
from django.db.models import F, Sum, Count, Min, Max
from ventas.models import DetalleVenta


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_mantenimiento(request):
    data = request.data.copy()
    data['cliente'] = request.user.id  # cliente autenticado
    data['estado'] = 'pendiente'       # estado inicial

    # ⚠️ no exigir técnico
    serializer = MantenimientoSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'mensaje': 'Solicitud registrada exitosamente.',
            'mantenimiento': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mantenimientos(request):
    """
    Devuelve todos los mantenimientos. 
    Los técnicos solo ven los asignados a ellos.
    """
    user = request.user

    if hasattr(user, 'tecnico'):
        mantenimientos = Mantenimiento.objects.filter(tecnico=user.tecnico)
    else:
        mantenimientos = Mantenimiento.objects.all().order_by('-fecha')

    serializer = MantenimientoSerializer(mantenimientos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class AsignarTecnicoView(APIView):
    """
    Solo los administradores pueden asignar técnicos a mantenimientos pendientes.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        usuario = request.user

        # Solo administradores pueden asignar técnicos
        if not usuario.rol or usuario.rol.nombre.lower() != 'administrador':
            return Response(
                {'error': 'No tiene permisos para asignar técnicos.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            mantenimiento = Mantenimiento.objects.get(id=id, estado='pendiente')
        except Mantenimiento.DoesNotExist:
            return Response(
                {'error': 'Mantenimiento no encontrado o ya asignado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        tecnico_id = request.data.get('tecnico')
        if not tecnico_id:
            return Response(
                {'error': 'Debe proporcionar el ID del técnico.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tecnico = Tecnico.objects.get(id=tecnico_id)
        except Tecnico.DoesNotExist:
            return Response(
                {'error': 'El técnico especificado no existe.'},
                status=status.HTTP_404_NOT_FOUND
            )

        mantenimiento.tecnico = tecnico
        mantenimiento.estado = 'en proceso'
        mantenimiento.save()

        return Response({
            'mensaje': f'Técnico {tecnico.nombre} asignado correctamente al mantenimiento #{id}.',
            'mantenimiento': {
                'id': mantenimiento.id,
                'descripcion': mantenimiento.descripcion,
                'tecnico_id': tecnico.id,
                'tecnico_nombre': tecnico.nombre,
                'estado': mantenimiento.estado
            }
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mantenimientos_por_tecnico(request):
    usuario = request.user

    # Verificar que el usuario sea técnico
    if not usuario.rol or usuario.rol.nombre.lower() != 'técnico':
        return Response(
            {'error': 'Solo los técnicos pueden ver sus mantenimientos.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Filtrar mantenimientos asignados al técnico actual
    mantenimientos = Mantenimiento.objects.filter(tecnico__usuario=usuario).order_by('-fecha')

    serializer = MantenimientoSerializer(mantenimientos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_estado_mantenimiento(request, id):
    usuario = request.user

    try:
        mantenimiento = Mantenimiento.objects.get(id=id)
    except Mantenimiento.DoesNotExist:
        return Response({'error': 'Mantenimiento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    # Validar que el usuario sea técnico
    if not usuario.rol or usuario.rol.nombre.lower() != 'técnico':
        return Response(
            {'error': 'Solo los técnicos pueden actualizar el estado de un mantenimiento.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Validar que este técnico sea el asignado
    if mantenimiento.tecnico is None or mantenimiento.tecnico.usuario.id != usuario.id:
        return Response(
            {'error': 'No tiene permiso para modificar este mantenimiento.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Obtener el nuevo estado
    nuevo_estado = request.data.get('estado')
    if nuevo_estado not in ['pendiente', 'en proceso', 'completado']:
        return Response({'error': 'Estado no válido. Use: pendiente, en proceso o completado.'},
                        status=status.HTTP_400_BAD_REQUEST)

    mantenimiento.estado = nuevo_estado
    mantenimiento.save()

    return Response({
        'mensaje': f'Estado actualizado a "{nuevo_estado}".',
        'mantenimiento': {
            'id': mantenimiento.id,
            'descripcion': mantenimiento.descripcion,
            'estado': mantenimiento.estado
        }
    }, status=status.HTTP_200_OK)

##Reporte

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_reporte_dinamico(request):
    prompt = request.data.get("prompt", "").lower()
    usuario = request.user

    if not prompt:
        return JsonResponse({"error": "Debe enviar un prompt de texto."}, status=400)

    # 🎯 1. Detectar formato
    formato = "pantalla"
    if "pdf" in prompt:
        formato = "pdf"
    elif "excel" in prompt or "xlsx" in prompt:
        formato = "excel"

    # 🔍 2. Base del queryset
    queryset = Venta.objects.all().select_related("cliente")

    # 📅 3. Filtro por fechas o meses
    # Detectar fechas tipo 01/10/2024 o 2024-10-01
    fecha_match = re.findall(r"\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}", prompt)
    if len(fecha_match) == 2:
        try:
            fecha_inicio = datetime.strptime(fecha_match[0], "%d/%m/%Y") if "/" in fecha_match[0] else datetime.strptime(fecha_match[0], "%Y-%m-%d")
            fecha_fin = datetime.strptime(fecha_match[1], "%d/%m/%Y") if "/" in fecha_match[1] else datetime.strptime(fecha_match[1], "%Y-%m-%d")
            queryset = queryset.filter(fecha__range=[fecha_inicio, fecha_fin])
        except Exception:
            pass
    else:
        # Filtro por mes textual (ej: "septiembre")
        meses = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5,
            "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10,
            "noviembre": 11, "diciembre": 12
        }
        for mes, num in meses.items():
            if mes in prompt:
                queryset = queryset.filter(fecha__month=num)

    # 💰 4. Filtro por monto (opcional)
    monto_match = re.search(r'(\d+(?:\.\d+)?)', prompt)
    if monto_match:
        monto = float(monto_match.group(1))
        if "menor" in prompt or "inferior" in prompt:
            queryset = queryset.filter(total__lt=monto)
        elif "mayor" in prompt or "superior" in prompt:
            queryset = queryset.filter(total__gt=monto)

    # 👤 5. Filtro por cliente específico
    cliente_match = re.search(r"cliente\s+([\wáéíóúñ]+)", prompt)
    if cliente_match:
        nombre_cliente = cliente_match.group(1)
        queryset = queryset.filter(cliente__cliente__nombre__icontains=nombre_cliente)

    # 📊 6. Generar datos según agrupación
    data = []

    # === AGRUPADO POR PRODUCTO ===
    if "agrupado por producto" in prompt:
        productos = (
            DetalleVenta.objects
            .values(nombre=F("producto__nombre"))
            .annotate(total_vendido=Sum("venta__total"), cantidad_vendida=Count("venta"))
        )
        for p in productos:
            data.append({
                "producto": p["nombre"],
                "cantidad_vendida": int(p["cantidad_vendida"] or 0),
                "total_vendido": float(p["total_vendido"] or 0),
            })

    # === AGRUPADO POR CLIENTE ===
    elif "agrupado por cliente" in prompt or "por cliente" in prompt:
        clientes = (
            queryset
            .values(nombre=F("cliente__cliente__nombre"))
            .annotate(cantidad_compras=Count("id"), total_vendido=Sum("total"), fecha_min=Min("fecha"), fecha_max=Max("fecha"))
        )
        for c in clientes:
            data.append({
                "cliente": c["nombre"],
                "cantidad_compras": c["cantidad_compras"],
                "total_vendido": float(c["total_vendido"] or 0),
                "rango_fechas": f"{c['fecha_min'].strftime('%Y-%m-%d')} → {c['fecha_max'].strftime('%Y-%m-%d')}"
            })

    # === SIN AGRUPACIÓN ===
    else:
        for venta in queryset:
            data.append({
                "cliente": venta.cliente.cliente.nombre if venta.cliente else "Sin cliente",
                "total_vendido": float(venta.total),
                "fecha": venta.fecha.strftime("%Y-%m-%d"),
            })

    if not data:
        return JsonResponse({"mensaje": "No hay datos para generar el reporte."}, status=200)

    # 🧾 7. Generar salida según formato
    if formato == "pdf":
        pdf_buffer = generar_pdf(data)
        return FileResponse(pdf_buffer, as_attachment=True, filename="reporte.pdf", content_type="application/pdf")
    elif formato == "excel":
        excel_buffer = generar_excel(data)
        return FileResponse(excel_buffer, as_attachment=True, filename="reporte.xlsx", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    return JsonResponse({"reporte": data}, safe=False)














