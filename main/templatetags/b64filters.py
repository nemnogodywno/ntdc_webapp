import base64
import os
from django import template

register = template.Library()

@register.filter
def b64encode(value):
    """Base64-кодирование для использования в шаблонах.

    Поддерживает:
    - bytes
    - str (кодируется как utf-8)
    - Django File/ImageFieldFile (читается содержимое файла)
    """
    if not value:
        return ''

    # Если это уже bytes
    if isinstance(value, (bytes, bytearray)):
        data = bytes(value)
    # Если это строка
    elif isinstance(value, str):
        data = value.encode('utf-8')
    else:
        # Пытаемся работать как с Django File/ImageFieldFile
        file_obj = getattr(value, 'file', value)
        try:
            data = file_obj.read()
        except Exception:
            # На крайний случай – приводим к строке
            data = str(value).encode('utf-8')

    return base64.b64encode(data).decode('utf-8')


@register.filter
def basename(value):
    """Вернуть только имя файла без пути для FileField/ImageField или строки пути."""
    if not value:
        return ''
    # Если это объект FileField/ImageField, берём .name
    name = getattr(value, 'name', value)
    return os.path.basename(str(name))
