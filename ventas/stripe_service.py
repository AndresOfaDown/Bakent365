# Servicio de integración con Stripe para pagos
import stripe
from django.conf import settings

# Configurar Stripe con la clave secreta
stripe.api_key = "sk_test_51SOpP3D9rf9HDuNtlFTbuMSNpxtCON5rsRaXSwW4OcUOgpMs07YVesOBj7H95R9STFVtUWweMd1TW5cFOt1f6i8B00MOUL08zX"

print(f"🔑 Stripe API Key configurada: {stripe.api_key[:20]}...{stripe.api_key[-4:]}")


def crear_payment_intent(monto, moneda="usd", metadata=None):
    """
    Crea un PaymentIntent en Stripe
    
    Args:
        monto (int): Monto en la unidad de la moneda (ej: 10.00 = $10.00)
        moneda (str): Código de moneda (usd, bob, etc.)
        metadata (dict): Datos adicionales para el pago
    
    Returns:
        dict: Información del PaymentIntent creado
    """
    try:
        # Convertir a centavos (Stripe requiere enteros)
        monto_centavos = int(round(float(monto) * 100))
        
        # Validar que el monto sea positivo
        if monto_centavos <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        
        payment_intent = stripe.PaymentIntent.create(
            amount=monto_centavos,
            currency=moneda.lower(),
            metadata=metadata or {},
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        return {
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
            'amount': payment_intent.amount,
            'status': payment_intent.status
        }
    except stripe._error.StripeError as e:
        # Log del error específico de Stripe
        print(f"❌ Error de Stripe: {str(e)}")
        raise Exception(f"Error de Stripe: {str(e)}")
    except Exception as e:
        # Log de cualquier otro error
        print(f"❌ Error general: {str(e)}")
        raise Exception(f"Error al crear PaymentIntent: {str(e)}")


def confirmar_pago(payment_intent_id):
    """
    Confirma que un pago fue exitoso
    
    Args:
        payment_intent_id (str): ID del PaymentIntent
    
    Returns:
        dict: Estado del pago
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return {
            'id': payment_intent.id,
            'status': payment_intent.status,
            'amount': payment_intent.amount / 100,  # Convertir a unidades
            'paid': payment_intent.status == 'succeeded'
        }
    except stripe._error.StripeError as e:
        raise Exception(f"Error al confirmar pago: {str(e)}")


def crear_customer(email, nombre=None):
    """
    Crea un cliente en Stripe
    
    Args:
        email (str): Email del cliente
        nombre (str): Nombre del cliente
    
    Returns:
        str: ID del cliente creado
    """
    try:
        customer = stripe.Customer.create(
            email=email,
            name=nombre
        )
        return customer.id
    except stripe._error.StripeError as e:
        raise Exception(f"Error al crear cliente: {str(e)}")
