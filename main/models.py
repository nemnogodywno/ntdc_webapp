from django.db import models

# Справочники
class PartType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название типа')
    def __str__(self):
        return self.name

class Operation(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название операции')
    def __str__(self):
        return self.name

class UserJob(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название должности')
    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название статуса')
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название склада')
    desc = models.TextField(blank=True, verbose_name='Описание')
    def __str__(self):
        return self.name

# Рабочие таблицы
class Part(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название узла')
    serial = models.CharField(max_length=255, blank=True, null=True, verbose_name='Серийный номер')
    decimal_num = models.CharField(max_length=255, verbose_name='Децимальный номер')
    desc = models.TextField(blank=True, verbose_name='Описание')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Родительский узел')
    type = models.ForeignKey(PartType, on_delete=models.CASCADE, verbose_name='Тип')
    image = models.BinaryField(blank=True, null=True, verbose_name='Фото', editable=True)
    is_used = models.BooleanField(default=False, verbose_name='Используется')
    def __str__(self):
        return f"{self.name} ({self.decimal_num})"

class Device(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Название устройства')
    serial = models.CharField(max_length=255, verbose_name='Серийный номер')
    desc = models.TextField(blank=True, verbose_name='Описание')
    parts = models.ManyToManyField(Part, verbose_name='Модели/Узлы', blank=True)
    image = models.BinaryField(blank=True, null=True, verbose_name='Фото', editable=True)
    is_used = models.BooleanField(default=False, verbose_name='Используется')
    def __str__(self):
        return f"{self.name or ''} ({self.serial})"

class User(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя')
    partonymic = models.CharField(max_length=255, verbose_name='Отчество')
    surname = models.CharField(max_length=255, verbose_name='Фамилия')
    job = models.ForeignKey(UserJob, on_delete=models.CASCADE, verbose_name='Должность')
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
    def __str__(self):
        return f"{self.device} - {self.operation} ({self.time:%d.%m.%Y %H:%M})"
