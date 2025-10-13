from django.contrib import admin
from .models import (
    AstralType, AstralVariant, AstralPart, AstralRevision, AstralYear, AstralManufacturer,
    MaterialPart, MaterialGroup, MaterialOperationType, MaterialUser, MaterialStatus,
    MaterialWarehouse, MaterialOperations
)

# ============== АСТРАЛЬНАЯ ЧАСТЬ ==============

@admin.register(AstralType)
class AstralTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')


@admin.register(AstralVariant)
class AstralVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'astral_type')
    search_fields = ('name', 'code')
    list_filter = ('astral_type',)


@admin.register(AstralPart)
class AstralPartAdmin(admin.ModelAdmin):
    list_display = ('name', 'decimal_num', 'astral_variant')
    search_fields = ('name', 'decimal_num')
    list_filter = ('astral_variant',)


@admin.register(AstralRevision)
class AstralRevisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_astral_parts', 'release_date', 'parent')
    search_fields = ('name',)
    list_filter = ('release_date',)
    date_hierarchy = 'release_date'
    filter_horizontal = ('astral_parts',)

    def get_astral_parts(self, obj):
        return ", ".join([part.name for part in obj.astral_parts.all()[:3]])
    get_astral_parts.short_description = 'Астральные узлы'


@admin.register(AstralYear)
class AstralYearAdmin(admin.ModelAdmin):
    list_display = ('astral_variant', 'year')
    search_fields = ('astral_variant__name',)
    list_filter = ('year',)


@admin.register(AstralManufacturer)
class AstralManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')


# ============== МАТЕРИАЛЬНАЯ ЧАСТЬ ==============

@admin.register(MaterialPart)
class MaterialPartAdmin(admin.ModelAdmin):
    list_display = ('serial', 'astral_revision', 'astral_year', 'astral_manufacturer', 'parent')
    search_fields = ('serial', 'astral_revision__name')
    list_filter = ('astral_year', 'astral_manufacturer')


@admin.register(MaterialGroup)
class MaterialGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(MaterialOperationType)
class MaterialOperationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'material_group', 'description')
    search_fields = ('name',)
    list_filter = ('material_group',)


@admin.register(MaterialUser)
class MaterialUserAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'first_name', 'second_name', 'material_group')
    search_fields = ('first_name', 'second_name', 'patronymic')
    list_filter = ('material_group',)

    def get_full_name(self, obj):
        return str(obj)
    get_full_name.short_description = 'ФИО'


@admin.register(MaterialStatus)
class MaterialStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(MaterialWarehouse)
class MaterialWarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    search_fields = ('name',)
    list_filter = ('parent',)


@admin.register(MaterialOperations)
class MaterialOperationsAdmin(admin.ModelAdmin):
    list_display = ('material_operation_type', 'material_part', 'material_user', 'datetime', 'material_status', 'material_warehouse')
    search_fields = ('material_part__serial', 'description')
    list_filter = ('material_operation_type', 'material_status', 'material_warehouse', 'datetime')
    date_hierarchy = 'datetime'
