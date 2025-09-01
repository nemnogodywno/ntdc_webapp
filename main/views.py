from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Device, Part, Journal, PartType, Operation, Status, Location, User
from .forms import DeviceForm, JournalForm, PartForm
from .qr_utils import get_device_url_qr, get_device_info_qr, get_part_url_qr, get_part_info_qr

def is_admin(user):
    """Проверка, является ли пользователь администратором"""
    return user.is_staff or user.is_superuser

def home_view(request):
    """Главная страница - доступна всем"""
    return render(request, 'main/home.html')

@login_required
def dashboard_view(request):
    """Панель управления - только для авторизованных"""
    context = {
        'user': request.user,
    }
    return render(request, 'main/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_panel_view(request):
    """Админ панель - только для администраторов"""
    return render(request, 'main/admin_panel.html')

@login_required
def devices_list(request):
    """Список всех устройств"""
    search_query = request.GET.get('search', '')
    devices = Device.objects.prefetch_related('parts', 'parts__type').all()

    if search_query:
        devices = devices.filter(
            Q(serial__icontains=search_query) |
            Q(parts__name__icontains=search_query) |
            Q(parts__decimal_num__icontains=search_query)
        ).distinct()

    context = {
        'devices': devices,
        'search_query': search_query,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/devices_list.html', context)

@login_required
def device_detail(request, device_id):
    """Детальная страница устройства с историей операций"""
    device = get_object_or_404(Device, id=device_id)
    journal_entries = Journal.objects.filter(device=device).select_related(
        'operation', 'user', 'status', 'location'
    ).order_by('-time')

    # Получаем компоненты (дочерние части) для всех частей устройства
    child_parts = Part.objects.filter(parent__in=device.parts.all()).distinct()

    # Генерируем QR-коды
    url_qr = get_device_url_qr(device, request)
    info_qr = get_device_info_qr(device)

    context = {
        'device': device,
        'journal_entries': journal_entries,
        'child_parts': child_parts,
        'is_admin': is_admin(request.user),
        'url_qr': url_qr,
        'info_qr': info_qr
    }
    return render(request, 'main/device_detail.html', context)

@login_required
@user_passes_test(is_admin)
def device_edit(request, device_id):
    """Редактирование устройства (только для админов)"""
    device = get_object_or_404(Device, id=device_id)

    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, f'Устройство {device.serial} успешно обновлено')
            return redirect('main:device_detail', device_id=device.id)
    else:
        form = DeviceForm(instance=device)

    context = {
        'form': form,
        'device': device,
        'title': f'Редактирование устройства {device.serial}'
    }
    return render(request, 'main/device_form.html', context)

@login_required
@user_passes_test(is_admin)
def device_create(request):
    """Создание нового устройства (только для админов)"""
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            messages.success(request, f'Устройство {device.serial} успешно создано')
            return redirect('main:device_detail', device_id=device.id)
    else:
        form = DeviceForm()

    context = {
        'form': form,
        'title': 'Создание нового устройства'
    }
    return render(request, 'main/device_form.html', context)

@login_required
@user_passes_test(is_admin)
def device_delete(request, device_id):
    """Удаление устройства (только для админов)"""
    device = get_object_or_404(Device, id=device_id)

    if request.method == 'POST':
        serial = device.serial
        device.delete()
        messages.success(request, f'Устройство {serial} успешно удалено')
        return redirect('main:devices_list')

    context = {
        'device': device,
        'title': f'Удаление устройства {device.serial}'
    }
    return render(request, 'main/device_confirm_delete.html', context)

@login_required
def journal_list(request):
    """Список всех записей истории операций"""
    search_query = request.GET.get('search', '')
    device_filter = request.GET.get('device', '')
    operation_filter = request.GET.get('operation', '')
    status_filter = request.GET.get('status', '')

    journal_entries = Journal.objects.select_related(
        'device', 'operation', 'user', 'status', 'location'
    ).prefetch_related('device__parts').order_by('-time')

    # Применяем фильтры
    if search_query:
        journal_entries = journal_entries.filter(
            Q(device__serial__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(result__icontains=search_query) |
            Q(user__surname__icontains=search_query)
        )

    if device_filter:
        journal_entries = journal_entries.filter(device_id=device_filter)

    if operation_filter:
        journal_entries = journal_entries.filter(operation_id=operation_filter)

    if status_filter:
        journal_entries = journal_entries.filter(status_id=status_filter)

    # Получаем данные для фильтров
    devices = Device.objects.prefetch_related('parts').all()
    operations = Operation.objects.all()
    statuses = Status.objects.all()

    context = {
        'journal_entries': journal_entries,
        'search_query': search_query,
        'device_filter': device_filter,
        'operation_filter': operation_filter,
        'status_filter': status_filter,
        'devices': devices,
        'operations': operations,
        'statuses': statuses,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/journal_list.html', context)

@login_required
def journal_detail(request, journal_id):
    """Детальная страница записи операции"""
    journal_entry = get_object_or_404(Journal, id=journal_id)

    context = {
        'journal_entry': journal_entry,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/journal_detail.html', context)

@login_required
@user_passes_test(is_admin)
def journal_create(request):
    """Создание новой записи операции (только для админов)"""
    if request.method == 'POST':
        form = JournalForm(request.POST)
        if form.is_valid():
            journal_entry = form.save()
            messages.success(request, f'Запись операции для устройства {journal_entry.device.serial} успешно создана')
            return redirect('main:journal_detail', journal_id=journal_entry.id)
    else:
        form = JournalForm()
        # Предустанавливаем текущее время
        from django.utils import timezone
        form.initial['time'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

    context = {
        'form': form,
        'title': 'Создание записи операции'
    }
    return render(request, 'main/journal_form.html', context)

@login_required
@user_passes_test(is_admin)
def journal_edit(request, journal_id):
    """Редактирование записи операции (только для админов)"""
    journal_entry = get_object_or_404(Journal, id=journal_id)

    if request.method == 'POST':
        form = JournalForm(request.POST, instance=journal_entry)
        if form.is_valid():
            form.save()
            messages.success(request, f'Запись операции для устройства {journal_entry.device.serial} успешно обновлена')
            return redirect('main:journal_detail', journal_id=journal_entry.id)
    else:
        form = JournalForm(instance=journal_entry)
        # Форматируем время для datetime-local
        form.initial['time'] = journal_entry.time.strftime('%Y-%m-%dT%H:%M')

    context = {
        'form': form,
        'journal_entry': journal_entry,
        'title': f'Редактирование записи операции'
    }
    return render(request, 'main/journal_form.html', context)

@login_required
@user_passes_test(is_admin)
def journal_delete(request, journal_id):
    """Удаление записи операции (только для админов)"""
    journal_entry = get_object_or_404(Journal, id=journal_id)

    if request.method == 'POST':
        device_serial = journal_entry.device.serial
        operation_name = journal_entry.operation.name
        journal_entry.delete()
        messages.success(request, f'Запись операции "{operation_name}" для устройства {device_serial} успешно удалена')
        return redirect('main:journal_list')

    context = {
        'journal_entry': journal_entry,
        'title': f'Удаление записи операции'
    }
    return render(request, 'main/journal_confirm_delete.html', context)

@login_required
def parts_list(request):
    """Список всех деталей/узлов"""
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')

    parts = Part.objects.select_related('type', 'parent').all()

    if search_query:
        parts = parts.filter(
            Q(name__icontains=search_query) |
            Q(decimal_num__icontains=search_query) |
            Q(desc__icontains=search_query)
        )

    if type_filter:
        parts = parts.filter(type_id=type_filter)

    # Получаем типы для фильтра
    part_types = PartType.objects.all()

    context = {
        'parts': parts,
        'search_query': search_query,
        'type_filter': type_filter,
        'part_types': part_types,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/parts_list.html', context)

@login_required
def part_detail(request, part_id):
    """Детальная страница детали/узла"""
    part = get_object_or_404(Part, id=part_id)

    # Получаем дочерние части
    child_parts = Part.objects.filter(parent=part).select_related('type')

    # Получаем устройства, которые используют эту деталь
    devices_using = Device.objects.filter(parts=part).prefetch_related('parts')

    # Генерируем QR-коды
    url_qr = get_part_url_qr(part, request)
    info_qr = get_part_info_qr(part)

    context = {
        'part': part,
        'child_parts': child_parts,
        'devices_using': devices_using,
        'is_admin': is_admin(request.user),
        'url_qr': url_qr,
        'info_qr': info_qr
    }
    return render(request, 'main/part_detail.html', context)

@login_required
@user_passes_test(is_admin)
def part_create(request):
    """Создание новой детали/узла (только для админов)"""
    if request.method == 'POST':
        form = PartForm(request.POST)
        if form.is_valid():
            part = form.save()
            messages.success(request, f'Деталь/узел "{part.name}" успешно создан')
            return redirect('main:part_detail', part_id=part.id)
    else:
        form = PartForm()

    context = {
        'form': form,
        'title': 'Создание новой детали/узла'
    }
    return render(request, 'main/part_form.html', context)

@login_required
@user_passes_test(is_admin)
def part_edit(request, part_id):
    """Редактирование детали/узла (только для админов)"""
    part = get_object_or_404(Part, id=part_id)

    if request.method == 'POST':
        form = PartForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            messages.success(request, f'Деталь/узел "{part.name}" успешно обновлен')
            return redirect('main:part_detail', part_id=part.id)
    else:
        form = PartForm(instance=part)

    context = {
        'form': form,
        'part': part,
        'title': f'Редактирование детали/узла "{part.name}"'
    }
    return render(request, 'main/part_form.html', context)

@login_required
@user_passes_test(is_admin)
def part_delete(request, part_id):
    """Удаление детали/узла (только для админов)"""
    part = get_object_or_404(Part, id=part_id)

    if request.method == 'POST':
        name = part.name
        part.delete()
        messages.success(request, f'Деталь/узел "{name}" успешно удален')
        return redirect('main:parts_list')

    # Проверяем, используется ли деталь в устройствах или как родительская
    devices_using = Device.objects.filter(parts=part).count()
    child_parts_count = Part.objects.filter(parent=part).count()

    context = {
        'part': part,
        'devices_using_count': devices_using,
        'child_parts_count': child_parts_count,
        'title': f'Удаление детали/узла "{part.name}"'
    }
    return render(request, 'main/part_confirm_delete.html', context)
