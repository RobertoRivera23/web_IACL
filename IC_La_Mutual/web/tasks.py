from celery import shared_task
from django.core.mail import send_mail
from .models import Notificacion

@shared_task
def enviar_notificacion_email(notificacion_id):
    notificacion = Notificacion.objects.get(id=notificacion_id)
    
    send_mail(
        'Nueva notificación disponible',
        f'Tienes una nueva notificación: {notificacion.mensaje}',
        'notificaciones@tudominio.com',
        [notificacion.cliente.usuario.email],
        fail_silently=False,
    )
    notificacion.leida = True
    notificacion.save()