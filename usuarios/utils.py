
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


from pyfcm import FCMNotification
from django.conf import settings

def enviar_notificacion_push(usuario, titulo, mensaje):
    if not usuario.fcm_token:
        print(f" El usuario {usuario.email} no tiene token FCM registrado.")
        return

    push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)
    result = push_service.notify_single_device(
        registration_id=usuario.fcm_token,
        message_title=titulo,
        message_body=mensaje,
        sound="default"
    )
    print("Notificación push enviada:", result)
