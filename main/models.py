from django.db import models

# Справочники
class PartType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название типа')

    class Meta:
        db_table = 'part_type'
        verbose_name = 'Тип устройства'
        verbose_name_plural = 'Типы устройств'

    def __str__(self):
        return self.name

class Operation(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название операции')

    class Meta:
        db_table = 'operation'
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'

    def __str__(self):
        return self.name

class UserJob(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название должности')

    class Meta:
        db_table = 'user_job'
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название статуса')

    class Meta:
        db_table = 'status'
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название склада')
    desc = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        db_table = 'location'
        verbose_name = 'Склад/Подразделение'
        verbose_name_plural = 'Склады/Подразделения'

    def __str__(self):
        return self.name

# Рабочие таблицы
class Part(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название узла')
    decimal_num = models.CharField(max_length=255, verbose_name='Децимальный номер')
    desc = models.TextField(blank=True, verbose_name='Описание')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Родительский узел')
    type = models.ForeignKey(PartType, on_delete=models.CASCADE, verbose_name='Тип')

    class Meta:
        db_table = 'parts'
        verbose_name = 'Модель/Узел'
        verbose_name_plural = 'Модели/Узлы'

    def __str__(self):
        return self.name

class Device(models.Model):
    serial = models.CharField(max_length=255, verbose_name='Серийный номер')
    desc = models.TextField(blank=True, verbose_name='Описание')
    parts = models.ManyToManyField(Part, verbose_name='Модели/Узлы', blank=True)

    class Meta:
        db_table = 'devices'
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'

    def __str__(self):
        parts_list = ', '.join([part.name for part in self.parts.all()[:3]])
        if self.parts.count() > 3:
            parts_list += '...'
        return f"{self.serial} ({parts_list})"

    @property
    def main_part(self):
        """Возвращает первую часть как основную"""
        return self.parts.first()

class User(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя')
    partonymic = models.CharField(max_length=255, verbose_name='Отчество')
    surname = models.CharField(max_length=255, verbose_name='Фамилия')
    job = models.ForeignKey(UserJob, on_delete=models.CASCADE, verbose_name='Должность')

    class Meta:
        db_table = 'user'
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f"{self.surname} {self.name} {self.partonymic}"

class Journal(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name='Устройство')
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, verbose_name='Операция')
    description = models.TextField(blank=True, verbose_name='Описание')
    result = models.TextField(blank=True, verbose_name='Результат')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Исполнитель')
    status = models.ForeignKey(Status, on_delete=models.CASCADE, verbose_name='Статус')
    time = models.DateTimeField(verbose_name='Дата/время')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='Место проведения')

    class Meta:
        db_table = 'journal'
        verbose_name = 'Запись журнала'
        verbose_name_plural = 'Записи журнала'
        ordering = ['-time']

    def __str__(self):
        return f"{self.device.serial} - {self.operation.name} ({self.time})"
