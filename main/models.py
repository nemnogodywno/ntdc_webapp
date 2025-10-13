from django.db import models

# ============== АСТРАЛЬНАЯ ЧАСТЬ (Справочники) ==============

class AstralType(models.Model):
    """Типы устройств (маршрутизаторы, коммутаторы, серверы)"""
    name = models.CharField(max_length=255, verbose_name='Название типа')
    code = models.CharField(max_length=255, unique=True, verbose_name='Код')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        db_table = 'astral_type'
        verbose_name = 'Астральный тип'
        verbose_name_plural = 'Астральные типы'


class AstralVariant(models.Model):
    """Варианты исполнения устройств"""
    name = models.CharField(max_length=255, verbose_name='Название варианта')
    code = models.CharField(max_length=255, unique=True, verbose_name='Код')
    description = models.TextField(blank=True, verbose_name='Описание')
    astral_type = models.ForeignKey(AstralType, on_delete=models.CASCADE, verbose_name='Астральный тип', related_name='variants')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        db_table = 'astral_variant'
        verbose_name = 'Астральный вариант'
        verbose_name_plural = 'Астральные варианты'


class AstralPart(models.Model):
    """Узлы устройств (базовые или уникальные)"""
    name = models.CharField(max_length=255, verbose_name='Название узла')
    decimal_num = models.CharField(max_length=255, unique=True, verbose_name='Децимальный номер')
    description = models.TextField(blank=True, verbose_name='Описание')
    astral_variant = models.ForeignKey(AstralVariant, on_delete=models.CASCADE, verbose_name='Астральный вариант', related_name='parts')

    def __str__(self):
        return f"{self.name} ({self.decimal_num})"

    class Meta:
        db_table = 'astral_part'
        verbose_name = 'Астральный узел'
        verbose_name_plural = 'Астральные узлы'


class AstralRevision(models.Model):
    """Ревизии (версии) узлов"""
    name = models.CharField(max_length=255, verbose_name='Название ревизии')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='astral_revisions/images/', blank=True, null=True, verbose_name='Изображение')
    file = models.FileField(upload_to='astral_revisions/', blank=True, null=True, verbose_name='Файл')
    astral_parts = models.ManyToManyField(AstralPart, verbose_name='Астральные узлы', related_name='revisions')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Родительская ревизия', related_name='children')
    release_date = models.DateField(null=True, blank=True, verbose_name='Дата выпуска')

    def __str__(self):
        parts_names = ", ".join([part.name for part in self.astral_parts.all()[:3]])
        if self.astral_parts.count() > 3:
            parts_names += "..."
        return f"{self.name} - {parts_names}"

    class Meta:
        db_table = 'astral_revision'
        verbose_name = 'Астральная ревизия'
        verbose_name_plural = 'Астральные ревизии'


class AstralYear(models.Model):
    """Привязка варианта к году выпуска"""
    astral_variant = models.ForeignKey(AstralVariant, on_delete=models.CASCADE, verbose_name='Астральный вариант', related_name='years')
    year = models.IntegerField(verbose_name='Год выпуска')

    def __str__(self):
        return f"{self.astral_variant.name} - {self.year}"

    class Meta:
        db_table = 'astral_year'
        verbose_name = 'Год выпуска астрального варианта'
        verbose_name_plural = 'Годы выпуска астральных вариантов'
        unique_together = [['astral_variant', 'year']]


class AstralManufacturer(models.Model):
    """Производители устройств"""
    name = models.CharField(max_length=255, verbose_name='Название производителя')
    code = models.CharField(max_length=255, unique=True, verbose_name='Код')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        db_table = 'astral_manufacturer'
        verbose_name = 'Астральный производитель'
        verbose_name_plural = 'Астральные производители'


# ============== МАТЕРИАЛЬНАЯ ЧАСТЬ (Рабочие таблицы) ==============

class MaterialPart(models.Model):
    """Реальный узел устройства с серийным номером"""
    serial = models.CharField(max_length=255, unique=True, verbose_name='Серийный номер')
    astral_revision = models.ForeignKey(AstralRevision, on_delete=models.PROTECT, verbose_name='Астральная ревизия', related_name='material_parts')
    astral_manufacturer = models.ForeignKey(AstralManufacturer, on_delete=models.PROTECT, verbose_name='Производитель', related_name='material_parts')
    astral_year = models.ForeignKey(AstralYear, on_delete=models.PROTECT, verbose_name='Год выпуска', related_name='material_parts')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Родительский узел', related_name='children')

    def __str__(self):
        parts = self.astral_revision.astral_parts.all()
        if parts.exists():
            part_name = parts.first().name
        else:
            part_name = "Без узла"
        return f"{part_name} (S/N: {self.serial})"

    class Meta:
        db_table = 'material_part'
        verbose_name = 'Материальный узел'
        verbose_name_plural = 'Материальные узлы'


class MaterialGroup(models.Model):
    """Группы операций"""
    name = models.CharField(max_length=255, verbose_name='Название группы')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'material_group'
        verbose_name = 'Группа операций'
        verbose_name_plural = 'Группы операций'


class MaterialOperationType(models.Model):
    """Типы операций (сборка, проверка и т.д.)"""
    name = models.CharField(max_length=255, verbose_name='Название операции')
    description = models.TextField(blank=True, verbose_name='Описание')
    material_group = models.ForeignKey(MaterialGroup, on_delete=models.CASCADE, verbose_name='Группа операций', related_name='operation_types')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'material_operation_type'
        verbose_name = 'Тип операции'
        verbose_name_plural = 'Типы операций'


class MaterialUser(models.Model):
    """Пользователи системы"""
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    second_name = models.CharField(max_length=255, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=255, blank=True, verbose_name='Отчество')
    material_group = models.ForeignKey(MaterialGroup, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Группа', related_name='users')

    def __str__(self):
        full_name = f"{self.second_name} {self.first_name}"
        if self.patronymic:
            full_name += f" {self.patronymic}"
        return full_name

    class Meta:
        db_table = 'material_user'
        verbose_name = 'Материальный пользователь'
        verbose_name_plural = 'Материальные пользователи'


class MaterialStatus(models.Model):
    """Статусы операций"""
    name = models.CharField(max_length=255, verbose_name='Название статуса')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'material_status'
        verbose_name = 'Материальный статус'
        verbose_name_plural = 'Материальные статусы'


class MaterialWarehouse(models.Model):
    """Склады (локации) с древовидной структурой"""
    name = models.CharField(max_length=255, verbose_name='Название склада')
    description = models.TextField(blank=True, verbose_name='Описание')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Родительский склад', related_name='children')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'material_warehouse'
        verbose_name = 'Материальный склад'
        verbose_name_plural = 'Материальные склады'


class MaterialOperations(models.Model):
    """Журнал операций"""
    material_operation_type = models.ForeignKey(MaterialOperationType, on_delete=models.PROTECT, verbose_name='Тип операции', related_name='operations')
    material_user = models.ForeignKey(MaterialUser, on_delete=models.PROTECT, verbose_name='Пользователь', related_name='operations')
    datetime = models.DateTimeField(verbose_name='Дата и время')
    description = models.TextField(blank=True, verbose_name='Описание')
    file = models.FileField(upload_to='material_operations/', blank=True, null=True, verbose_name='Файл')
    image = models.ImageField(upload_to='material_operations/images/', blank=True, null=True, verbose_name='Изображение')
    material_status = models.ForeignKey(MaterialStatus, on_delete=models.PROTECT, verbose_name='Статус', related_name='operations')
    material_warehouse = models.ForeignKey(MaterialWarehouse, on_delete=models.PROTECT, verbose_name='Склад', related_name='operations')
    material_part = models.ForeignKey(MaterialPart, on_delete=models.CASCADE, verbose_name='Материальный узел', related_name='operations')

    def __str__(self):
        return f"{self.material_operation_type.name} - {self.material_part.serial} ({self.datetime:%d.%m.%Y %H:%M})"

    class Meta:
        db_table = 'material_operations'
        verbose_name = 'Материальная операция'
        verbose_name_plural = 'Материальные операции'
        ordering = ['-datetime']
