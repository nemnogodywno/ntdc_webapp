import qrcode
import base64
from io import BytesIO
from django.conf import settings


def generate_qr_code(data, size=(200, 200)):
    """
    Генерирует QR-код и возвращает его в формате base64 для встраивания в HTML
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize(size)

    # Конвертируем в base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def get_device_url_qr(device, request):
    """
    Генерирует QR-код со ссылкой на страницу устройства
    """
    url = request.build_absolute_uri(f'/devices/{device.id}/')
    return generate_qr_code(url)


def get_device_info_qr(device):
    """
    Генерирует QR-код с текстовой информацией об устройстве для оффлайн чтения
    """
    parts_list = ', '.join([part.name for part in device.parts.all()])

    info_text = f"""УСТРОЙСТВО: {device.serial}
МОДЕЛИ/УЗЛЫ: {parts_list if parts_list else 'Не указано'}
ОПИСАНИЕ: {device.desc if device.desc else 'Не указано'}
СИСТЕМА: НТДЦ"""

    return generate_qr_code(info_text, size=(250, 250))


def get_part_url_qr(part, request):
    """
    Генерирует QR-код со ссылкой на страницу детали/узла
    """
    url = request.build_absolute_uri(f'/parts/{part.id}/')
    return generate_qr_code(url)


def get_part_info_qr(part):
    """
    Генерирует QR-код с текстовой информацией о детали/узле для оффлайн чтения
    """
    parent_info = f"РОДИТЕЛЬ: {part.parent.name}" if part.parent else "КОРНЕВОЙ УЗЕЛ"

    info_text = f"""ДЕТАЛЬ/УЗЕЛ: {part.name}
ДЕЦИМАЛЬНЫЙ №: {part.decimal_num}
ТИП: {part.type.name}
{parent_info}
ОПИСАНИЕ: {part.desc if part.desc else 'Не указано'}
СИСТЕМА: НТДЦ"""

    return generate_qr_code(info_text, size=(250, 250))
