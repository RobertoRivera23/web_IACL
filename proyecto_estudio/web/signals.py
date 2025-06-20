from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(pre_save, sender=DocumentoRequerido)
def registrar_cambios(sender, instance, **kwargs):
    if not instance.pk:  # Nuevo documento
        return
    
    original = DocumentoRequerido.objects.get(pk=instance.pk)
    
    cambios = {}
    if original.archivo != instance.archivo:
        cambios['archivo'] = {
            'de': str(original.archivo),
            'a': str(instance.archivo)
        }
    
    if original.completado != instance.completado:
        cambios['estado'] = {
            'de': original.completado,
            'a': instance.completado
        }
    
    if cambios:
        AuditoriaDocumento.objects.create(
            documento=instance,
            accion='UPLOAD' if 'archivo' in cambios else 'STATUS',
            detalle=cambios,
            usuario=instance.modified_by  # Asume campo modified_by en el modelo
        )