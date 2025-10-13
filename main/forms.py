from django import forms
from .models import (
    MaterialPart, MaterialOperations, AstralRevision, AstralPart
)


class MaterialPartForm(forms.ModelForm):
    """Форма для материального узла"""
    class Meta:
        model = MaterialPart
        fields = ['serial', 'astral_revision', 'astral_year', 'astral_manufacturer', 'parent']
        widgets = {
            'serial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Серийный номер'}),
            'astral_revision': forms.Select(attrs={'class': 'form-control'}),
            'astral_year': forms.Select(attrs={'class': 'form-control'}),
            'astral_manufacturer': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }


class MaterialOperationsForm(forms.ModelForm):
    """Форма для операций"""
    class Meta:
        model = MaterialOperations
        fields = ['material_operation_type', 'material_user', 'datetime', 'description',
                  'file', 'image', 'material_status', 'material_warehouse', 'material_part']
        widgets = {
            'material_operation_type': forms.Select(attrs={'class': 'form-control'}),
            'material_user': forms.Select(attrs={'class': 'form-control'}),
            'datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'material_status': forms.Select(attrs={'class': 'form-control'}),
            'material_warehouse': forms.Select(attrs={'class': 'form-control'}),
            'material_part': forms.Select(attrs={'class': 'form-control'}),
        }


class AstralRevisionForm(forms.ModelForm):
    """Форма для астральной ревизии"""
    class Meta:
        model = AstralRevision
        fields = ['name', 'description', 'file', 'image', 'astral_parts', 'parent', 'release_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название ревизии'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'astral_parts': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class AstralPartForm(forms.ModelForm):
    """Форма для астрального узла"""
    class Meta:
        model = AstralPart
        fields = ['name', 'decimal_num', 'astral_variant', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название узла'}),
            'decimal_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Децимальный номер'}),
            'astral_variant': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
