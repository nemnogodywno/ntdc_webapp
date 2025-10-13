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
    # Формируем список экземпляров деталей с серийными номерами
    part_instances = device.part_instances.all()
    if part_instances.exists():
        parts_list = ', '.join([f"{inst.part.name} (S/N: {inst.serial})" for inst in part_instances])
    else:
        parts_list = 'Не указано'

    device_name = device.name if device.name else device.serial

    info_text = f"""УСТРОЙСТВО: {device_name}
СЕРИЙНЫЙ №: {device.serial}
СОСТАВ: {parts_list}
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

    # Добавляем информацию о количестве экземпляров
    instances_count = part.instances.count()
    instances_info = f"ЭКЗЕМПЛЯРОВ: {instances_count}"

    info_text = f"""ДЕТАЛЬ/УЗЕЛ: {part.name}
ДЕЦИМАЛЬНЫЙ №: {part.decimal_num}
ТИП: {part.type.name}
{parent_info}
{instances_info}
ОПИСАНИЕ: {part.desc if part.desc else 'Не указано'}
СИСТЕМА: НТДЦ"""

    return generate_qr_code(info_text, size=(250, 250))


# ============== QR-коды для материальных узлов ==============

def get_material_part_url_qr(part, request):
    """
    Генерирует QR-код со ссылкой на страницу материального узла
    """
    url = request.build_absolute_uri(f'/material-parts/{part.id}/')
    return generate_qr_code(url)


def get_material_part_info_qr(part):
    """
    Генерирует QR-код с текстовой информацией о материальном узле для оффлайн чтения
    """
    astral_part = part.astral_revision.astral_parts.first()
    if not astral_part:
        astral_part_name = "Без узла"
        astral_type = "Не указан"
    else:
        astral_part_name = astral_part.name
        astral_type = astral_part.astral_variant.astral_type.name
    revision_name = part.astral_revision.name
    manufacturer = part.astral_manufacturer.name
    year = part.astral_year.year

    info_text = f"""МАТЕРИАЛЬНЫЙ УЗЕЛ
S/N: {part.serial}
УЗЕЛ: {astral_part_name}
ТИП: {astral_type}
РЕВИЗИЯ: {revision_name}
ПРОИЗВОДИТЕЛЬ: {manufacturer}
ГОД: {year}
СИСТЕМА: НТДЦ"""

    return generate_qr_code(info_text, size=(250, 250))


# ============== QR-коды для астральных ревизий ==============

def get_astral_revision_url_qr(revision, request):
    """
    Генерирует QR-код со ссылкой на страницу астральной ревизии
    """
    url = request.build_absolute_uri(f'/astral-revisions/{revision.id}/')
    return generate_qr_code(url)


def get_astral_revision_info_qr(revision):
    """
    Генерирует QR-код с текстовой информацией об астральной ревизии для оффлайн чтения
    """
    astral_part = revision.astral_parts.first()
    if not astral_part:
        astral_part_name = "Без узла"
        astral_type = "Не указан"
    else:
        astral_part_name = astral_part.name
        astral_type = astral_part.astral_variant.astral_type.name
    parent_info = f"РОДИТЕЛЬ: {revision.parent.name}" if revision.parent else "КОРНЕВАЯ РЕВИЗИЯ"
    release_date = revision.release_date.strftime("%d.%m.%Y") if revision.release_date else "Не указана"

    info_text = f"""АСТРАЛЬНАЯ РЕВИЗИЯ
НАЗВАНИЕ: {revision.name}
УЗЕЛ: {astral_part_name}
ТИП: {astral_type}
{parent_info}
ДАТА ВЫПУСКА: {release_date}
СИСТЕМА: НТДЦ"""

    return generate_qr_code(info_text, size=(250, 250))
