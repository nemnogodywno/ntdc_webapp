from django import forms
from .models import Device, Part, Journal, Operation, Status, Location, User, PartType

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['serial', 'desc', 'parts']
        widgets = {
            'serial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите серийный номер'
            }),
            'desc': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание устройства'
            }),
            'parts': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '10',
                'style': 'height: 200px;'
            })
        }
        labels = {
            'serial': 'Серийный номер',
            'desc': 'Описание',
            'parts': 'Модели/Узлы'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем возможность выбора всех частей с группировкой по типам
        self.fields['parts'].queryset = Part.objects.select_related('type').order_by('type__name', 'name')
        self.fields['parts'].help_text = 'Удерживайте Ctrl (Cmd на Mac) для выбора нескольких элементов'

        # Создаем красивый список с информацией о типе
        choices = []
        for part in self.fields['parts'].queryset:
            label = f"{part.name} ({part.type.name}) - {part.decimal_num}"
            choices.append((part.pk, label))
        self.fields['parts'].choices = choices

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'decimal_num', 'desc', 'parent', 'type']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название детали/узла'
            }),
            'decimal_num': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите децимальный номер'
            }),
            'desc': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание детали/узла'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'name': 'Название детали/узла',
            'decimal_num': 'Децимальный номер',
            'desc': 'Описание',
            'parent': 'Родительский узел',
            'type': 'Тип'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настраиваем выбор родительских узлов (исключаем саму деталь при редактировании)
        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = Part.objects.exclude(pk=self.instance.pk).select_related('type')
        else:
            self.fields['parent'].queryset = Part.objects.select_related('type').all()

        self.fields['parent'].empty_label = "Выберите родительский узел (опционально)"
        self.fields['type'].empty_label = "Выберите тип"

        # Добавляем информацию о типе в выбор родительского узла
        parent_choices = [(None, "Выберите родительский узел (опционально)")]
        for part in self.fields['parent'].queryset.order_by('type__name', 'name'):
            label = f"{part.name} ({part.type.name}) - {part.decimal_num}"
            parent_choices.append((part.pk, label))
        self.fields['parent'].choices = parent_choices

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ['device', 'operation', 'description', 'result', 'user', 'status', 'location', 'time']
        widgets = {
            'device': forms.Select(attrs={
                'class': 'form-control'
            }),
            'operation': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Подробное описание операции'
            }),
            'result': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Результат выполнения операции'
            }),
            'user': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
            'time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
        labels = {
            'device': 'Устройство',
            'operation': 'Операция',
            'description': 'Описание',
            'result': 'Результат',
            'user': 'Исполнитель',
            'status': 'Статус',
            'location': 'Место проведения',
            'time': 'Дата и время'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настраиваем выбор устройств с детальной информацией
        self.fields['device'].queryset = Device.objects.prefetch_related('parts').all()
        self.fields['device'].empty_label = "Выберите устройство"

        # Добавляем пустые варианты для обязательных полей
        self.fields['operation'].empty_label = "Выберите операцию"
        self.fields['user'].empty_label = "Выберите исполнителя"
        self.fields['status'].empty_label = "Выберите статус"
        self.fields['location'].empty_label = "Выберите место"
