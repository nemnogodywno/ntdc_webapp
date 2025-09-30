from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from .models import Device, Part, Journal

@receiver(m2m_changed, sender=Device.parts.through)
def update_part_is_used(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Обновляем is_used для всех частей
        for part in Part.objects.all():
            part.is_used = part.device_set.exists()
            part.save(update_fields=['is_used'])

@receiver(post_save, sender=Journal)
def update_device_is_used_on_journal_save(sender, instance, **kwargs):
    device = instance.device
    device.is_used = Journal.objects.filter(device=device).exists()
    device.save(update_fields=['is_used'])

@receiver(post_delete, sender=Journal)
def update_device_is_used_on_journal_delete(sender, instance, **kwargs):
    device = instance.device
    device.is_used = Journal.objects.filter(device=device).exists()
    device.save(update_fields=['is_used'])

