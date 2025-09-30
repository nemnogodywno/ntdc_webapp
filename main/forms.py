from django import forms
from .models import Device, Part, Journal, Operation, Status, Location, User, PartType

class DeviceForm(forms.ModelForm):
    image = forms.FileField(required=False, label='Фото устройства')
    class Meta:
        model = Device
        fields = ['name', 'serial', 'desc', 'parts', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название устройства'
            }),
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
            'name': 'Название устройства',
            'serial': 'Серийный номер',
            'desc': 'Описание',
            'parts': 'Модели/Узлы',
            'image': 'Фото устройства',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parts'].queryset = Part.objects.filter(is_used=False).select_related('type').order_by('type__name', 'name')
        self.fields['parts'].help_text = 'Удерживайте Ctrl (Cmd на Mac) для выбора нескольких элементов'
        choices = []
        for part in self.fields['parts'].queryset:
            label = f"{part.name} ({part.type.name}) - {part.decimal_num}"
            choices.append((part.pk, label))
        self.fields['parts'].choices = choices

class PartForm(forms.ModelForm):
    image = forms.FileField(required=False, label='Фото детали/узла')
    class Meta:
        model = Part
        fields = ['name', 'serial', 'decimal_num', 'desc', 'parent', 'type', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название детали/узла'
            }),
            'serial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите серийный номер'
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
            'serial': 'Серийный номер',
            'decimal_num': 'Децимальный номер',
            'desc': 'Описание',
            'parent': 'Родительский узел',
            'type': 'Тип',
            'image': 'Фото детали/узла',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # parent можно выбрать любой, кроме самого себя
        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = Part.objects.exclude(pk=self.instance.pk).select_related('type')
        else:
            self.fields['parent'].queryset = Part.objects.select_related('type').all()
        self.fields['parent'].empty_label = "Выберите родительский узел (опционально)"
        self.fields['type'].empty_label = "Выберите тип"
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
