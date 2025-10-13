from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from .models import (
    MaterialPart, MaterialOperations, AstralRevision, AstralPart, AstralType,
    AstralVariant, AstralYear, AstralManufacturer, MaterialStatus, MaterialWarehouse,
    MaterialOperationType, MaterialUser, MaterialGroup
)
from .forms import MaterialPartForm, MaterialOperationsForm, AstralRevisionForm
from .qr_utils import get_material_part_url_qr, get_material_part_info_qr, get_astral_revision_url_qr, get_astral_revision_info_qr


def is_admin(user):
    """Проверка, является ли пользователь администратором"""
    return user.is_staff or user.is_superuser


def home_view(request):
    """Главная страница"""
    context = {
        'total_parts': MaterialPart.objects.count(),
        'total_operations': MaterialOperations.objects.count(),
        'total_revisions': AstralRevision.objects.count(),
    }
    return render(request, 'main/home.html', context)


@login_required
def dashboard_view(request):
    """Панель управления"""
    context = {
        'user': request.user,
        'recent_operations': MaterialOperations.objects.select_related(
            'material_part', 'material_operation_type', 'material_status'
        ).order_by('-datetime')[:10],
    }
    return render(request, 'main/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_panel_view(request):
    """Админ панель"""
    context = {
        'astral_types': AstralType.objects.annotate(variants_count=Count('variants')).all(),
        'material_groups': MaterialGroup.objects.annotate(users_count=Count('users')).all(),
    }
    return render(request, 'main/admin_panel.html', context)


# ============== МАТЕРИАЛЬНЫЕ УЗЛЫ ==============

@login_required
def material_parts_list(request):
    """Список материальных узлов"""
    search_query = request.GET.get('search', '')
    manufacturer_filter = request.GET.get('manufacturer', '')
    year_filter = request.GET.get('year', '')

    parts = MaterialPart.objects.select_related(
        'astral_revision__astral_part__astral_variant__astral_type',
        'astral_year__astral_variant',
        'astral_manufacturer',
        'parent'
    ).all()

    if search_query:
        parts = parts.filter(
            Q(serial__icontains=search_query) |
            Q(astral_revision__name__icontains=search_query) |
            Q(astral_revision__astral_part__name__icontains=search_query)
        )

    if manufacturer_filter:
        parts = parts.filter(astral_manufacturer_id=manufacturer_filter)

    if year_filter:
        parts = parts.filter(astral_year__year=year_filter)

    context = {
        'parts': parts,
        'search_query': search_query,
        'manufacturers': AstralManufacturer.objects.all(),
        'years': AstralYear.objects.values_list('year', flat=True).distinct().order_by('-year'),
        'manufacturer_filter': manufacturer_filter,
        'year_filter': year_filter,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/material_parts_list.html', context)


@login_required
def material_part_detail(request, part_id):
    """Детальная информация о материальном узле"""
    part = get_object_or_404(
        MaterialPart.objects.select_related(
            'astral_revision__astral_part__astral_variant__astral_type',
            'astral_year__astral_variant',
            'astral_manufacturer',
            'parent'
        ).prefetch_related('children', 'operations'),
        pk=part_id
    )

    # Генерируем QR-коды
    qr_url = get_material_part_url_qr(part, request)
    qr_info = get_material_part_info_qr(part)

    context = {
        'part': part,
        'qr_url': qr_url,
        'qr_info': qr_info,
        'operations': part.operations.select_related(
            'material_operation_type', 'material_user', 'material_status', 'material_warehouse'
        ).order_by('-datetime')[:20],
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/material_part_detail.html', context)


@login_required
@user_passes_test(is_admin)
def material_part_create(request):
    """Создание материального узла"""
    if request.method == 'POST':
        form = MaterialPartForm(request.POST)
        if form.is_valid():
            part = form.save()
            messages.success(request, f'Материальный узел {part.serial} успешно создан!')
            return redirect('main:material_part_detail', part_id=part.id)
    else:
        form = MaterialPartForm()

    context = {
        'form': form,
        'title': 'Создание материального узла'
    }
    return render(request, 'main/material_part_form.html', context)


@login_required
@user_passes_test(is_admin)
def material_part_edit(request, part_id):
    """Редактирование материального узла"""
    part = get_object_or_404(MaterialPart, pk=part_id)

    if request.method == 'POST':
        form = MaterialPartForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            messages.success(request, f'Материальный узел {part.serial} успешно обновлен!')
            return redirect('main:material_part_detail', part_id=part.id)
    else:
        form = MaterialPartForm(instance=part)

    context = {
        'form': form,
        'part': part,
        'title': f'Редактирование {part.serial}'
    }
    return render(request, 'main/material_part_form.html', context)


@login_required
@user_passes_test(is_admin)
def material_part_delete(request, part_id):
    """Удаление материального узла"""
    part = get_object_or_404(MaterialPart, pk=part_id)

    if request.method == 'POST':
        serial = part.serial
        part.delete()
        messages.success(request, f'Материальный узел {serial} успешно удален!')
        return redirect('main:material_parts_list')

    context = {
        'part': part,
    }
    return render(request, 'main/material_part_confirm_delete.html', context)


# ============== ОПЕРАЦИИ ==============

@login_required
def operations_list(request):
    """Список операций (журнал)"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    operation_type_filter = request.GET.get('operation_type', '')

    operations = MaterialOperations.objects.select_related(
        'material_operation_type',
        'material_user',
        'material_part',
        'material_status',
        'material_warehouse'
    ).all()

    if search_query:
        operations = operations.filter(
            Q(material_part__serial__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if status_filter:
        operations = operations.filter(material_status_id=status_filter)

    if operation_type_filter:
        operations = operations.filter(material_operation_type_id=operation_type_filter)

    context = {
        'operations': operations,
        'search_query': search_query,
        'statuses': MaterialStatus.objects.all(),
        'operation_types': MaterialOperationType.objects.all(),
        'status_filter': status_filter,
        'operation_type_filter': operation_type_filter,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/operations_list.html', context)


@login_required
def operation_detail(request, operation_id):
    """Детальная информация об операции"""
    operation = get_object_or_404(
        MaterialOperations.objects.select_related(
            'material_operation_type',
            'material_user',
            'material_part__astral_revision__astral_part',
            'material_status',
            'material_warehouse'
        ),
        pk=operation_id
    )

    context = {
        'operation': operation,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/operation_detail.html', context)


@login_required
def operation_create(request):
    """Создание операции"""
    if request.method == 'POST':
        form = MaterialOperationsForm(request.POST, request.FILES)
        if form.is_valid():
            operation = form.save()
            messages.success(request, 'Операция успешно создана!')
            return redirect('main:operation_detail', operation_id=operation.id)
    else:
        form = MaterialOperationsForm()

    context = {
        'form': form,
        'title': 'Создание операции'
    }
    return render(request, 'main/operation_form.html', context)


@login_required
@user_passes_test(is_admin)
def operation_edit(request, operation_id):
    """Редактирование операции"""
    operation = get_object_or_404(MaterialOperations, pk=operation_id)

    if request.method == 'POST':
        form = MaterialOperationsForm(request.POST, request.FILES, instance=operation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Операция успешно обновлена!')
            return redirect('main:operation_detail', operation_id=operation.id)
    else:
        form = MaterialOperationsForm(instance=operation)

    context = {
        'form': form,
        'operation': operation,
        'title': 'Редактирование операции'
    }
    return render(request, 'main/operation_form.html', context)


@login_required
@user_passes_test(is_admin)
def operation_delete(request, operation_id):
    """Удаление операции"""
    operation = get_object_or_404(MaterialOperations, pk=operation_id)

    if request.method == 'POST':
        operation.delete()
        messages.success(request, 'Операция успешно удалена!')
        return redirect('main:operations_list')

    context = {
        'operation': operation,
    }
    return render(request, 'main/operation_confirm_delete.html', context)


# ============== АСТРАЛЬНЫЕ РЕВИЗИИ ==============

@login_required
def astral_revisions_list(request):
    """Список астральных ревизий"""
    search_query = request.GET.get('search', '')

    revisions = AstralRevision.objects.select_related(
        'astral_part__astral_variant__astral_type',
        'parent'
    ).all()

    if search_query:
        revisions = revisions.filter(
            Q(name__icontains=search_query) |
            Q(astral_part__name__icontains=search_query)
        )

    context = {
        'revisions': revisions,
        'search_query': search_query,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/astral_revisions_list.html', context)


@login_required
def astral_revision_detail(request, revision_id):
    """Детальная информация об астральной ревизии"""
    revision = get_object_or_404(
        AstralRevision.objects.select_related(
            'astral_part__astral_variant__astral_type',
            'parent'
        ).prefetch_related('material_parts'),
        pk=revision_id
    )

    # Генерируем QR-коды
    qr_url = get_astral_revision_url_qr(revision, request)
    qr_info = get_astral_revision_info_qr(revision)

    context = {
        'revision': revision,
        'qr_url': qr_url,
        'qr_info': qr_info,
        'material_parts': revision.material_parts.all()[:50],
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/astral_revision_detail.html', context)


@login_required
@user_passes_test(is_admin)
def astral_revision_create(request):
    """Создание астральной ревизии"""
    if request.method == 'POST':
        form = AstralRevisionForm(request.POST, request.FILES)
        if form.is_valid():
            revision = form.save()
            messages.success(request, f'Астральная ревизия {revision.name} успешно создана!')
            return redirect('main:astral_revision_detail', revision_id=revision.id)
    else:
        form = AstralRevisionForm()

    context = {
        'form': form,
        'title': 'Создание астральной ревизии'
    }
    return render(request, 'main/astral_revision_form.html', context)


@login_required
@user_passes_test(is_admin)
def astral_revision_edit(request, revision_id):
    """Редактирование астральной ревизии"""
    revision = get_object_or_404(AstralRevision, pk=revision_id)

    if request.method == 'POST':
        form = AstralRevisionForm(request.POST, request.FILES, instance=revision)
        if form.is_valid():
            form.save()
            messages.success(request, f'Астральная ревизия {revision.name} успешно обновлена!')
            return redirect('main:astral_revision_detail', revision_id=revision.id)
    else:
        form = AstralRevisionForm(instance=revision)

    context = {
        'form': form,
        'revision': revision,
        'title': f'Редактирование {revision.name}'
    }
    return render(request, 'main/astral_revision_form.html', context)


@login_required
@user_passes_test(is_admin)
def astral_revision_delete(request, revision_id):
    """Удаление астральной ревизии"""
    revision = get_object_or_404(AstralRevision, pk=revision_id)

    if request.method == 'POST':
        name = revision.name
        revision.delete()
        messages.success(request, f'Астральная ревизия {name} успешно удалена!')
        return redirect('main:astral_revisions_list')

    context = {
        'revision': revision,
    }
    return render(request, 'main/astral_revision_confirm_delete.html', context)


# ============== АСТРАЛЬНЫЕ УЗЛЫ ==============

@login_required
def astral_parts_list(request):
    """Список астральных узлов"""
    search_query = request.GET.get('search', '')
    variant_filter = request.GET.get('variant', '')

    parts = AstralPart.objects.select_related(
        'astral_variant__astral_type'
    ).prefetch_related('revisions').all()

    if search_query:
        parts = parts.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query)
        )

    if variant_filter:
        parts = parts.filter(astral_variant_id=variant_filter)

    context = {
        'parts': parts,
        'search_query': search_query,
        'variants': AstralVariant.objects.all(),
        'variant_filter': variant_filter,
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/astral_parts_list.html', context)


@login_required
def astral_part_detail(request, part_id):
    """Детальная информация об астральном узле"""
    part = get_object_or_404(
        AstralPart.objects.select_related(
            'astral_variant__astral_type'
        ).prefetch_related('revisions'),
        pk=part_id
    )

    context = {
        'part': part,
        'revisions': part.revisions.all(),
        'is_admin': is_admin(request.user)
    }
    return render(request, 'main/astral_part_detail.html', context)

