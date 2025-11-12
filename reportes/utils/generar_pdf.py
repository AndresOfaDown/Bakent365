from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generar_pdf(data):
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, y, "Reporte de Ventas")
    y -= 30
    c.setFont("Helvetica", 10)

    for item in data:
        cliente = item.get("cliente", "Sin cliente")
        cantidad = item.get("cantidad_compras", "")
        total = item.get("total_vendido") or item.get("monto_total") or item.get("total") or 0
        rango = item.get("rango_fechas", "")
        fecha = item.get("fecha", "")

        c.drawString(50, y, f"Cliente: {cliente}")
        y -= 15
        if cantidad:
            c.drawString(70, y, f"Compras: {cantidad}")
            y -= 15
        if rango:
            c.drawString(70, y, f"Rango: {rango}")
            y -= 15
        if fecha:
            c.drawString(70, y, f"Fecha: {fecha}")
            y -= 15
        c.drawString(70, y, f"Total: Bs {total}")
        y -= 25

        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    return buffer

