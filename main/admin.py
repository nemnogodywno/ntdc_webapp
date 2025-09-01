from django.contrib import admin
from .models import (
    PartType, Operation, UserJob, Status, Location,
    Part, Device, User, Journal
)

@admin.register(PartType)
class PartTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(UserJob)
class UserJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'desc']
    search_fields = ['name']

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'decimal_num', 'type', 'parent']
    list_filter = ['type']
    search_fields = ['name', 'decimal_num']
    list_select_related = ['type', 'parent']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'serial', 'get_parts', 'get_part_types']
    list_filter = ['parts__type']
    search_fields = ['serial', 'parts__name', 'parts__decimal_num']
    filter_horizontal = ['parts']  # Удобный виджет для ManyToMany

    def get_parts(self, obj):
        return ', '.join([part.name for part in obj.parts.all()[:3]]) + ('...' if obj.parts.count() > 3 else '')
    get_parts.short_description = 'Модели/Узлы'

    def get_part_types(self, obj):
        types = set([part.type.name for part in obj.parts.all()])
        return ', '.join(types)
    get_part_types.short_description = 'Типы'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'surname', 'name', 'partonymic', 'job']
    list_filter = ['job']
    search_fields = ['surname', 'name', 'partonymic']
    list_select_related = ['job']

@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'operation', 'user', 'status', 'time', 'location']
    list_filter = ['operation', 'status', 'location', 'time']
    search_fields = ['device__serial', 'user__surname', 'description']
    list_select_related = ['device', 'operation', 'user', 'status', 'location']
    date_hierarchy = 'time'
    ordering = ['-time']
