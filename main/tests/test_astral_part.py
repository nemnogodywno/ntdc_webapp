from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from main.models import AstralType, AstralVariant, AstralPart
from main.forms import AstralPartForm


class AstralPartTestBase(TestCase):
    def setUp(self):
        self.type = AstralType.objects.create(name='Тип A', code='T-A')
        self.variant = AstralVariant.objects.create(name='Вариант 1', code='V-1', astral_type=self.type)
        self.variant2 = AstralVariant.objects.create(name='Вариант 2', code='V-2', astral_type=self.type)
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
        self.user = User.objects.create_user(username='user', password='pass', is_staff=False)


class TestAstralPartModel(AstralPartTestBase):
    def test_decimal_num_is_required_model_validation(self):
        part = AstralPart(name='Узел X', astral_variant=self.variant)
        with self.assertRaises(IntegrityError):
            # Без decimal_num сохранение должно упасть на уровне БД (NOT NULL + unique)
            part.save()

    def test_decimal_num_must_be_unique(self):
        AstralPart.objects.create(name='Узел 1', decimal_num='1.2.3', astral_variant=self.variant)
        with self.assertRaises(IntegrityError):
            AstralPart.objects.create(name='Узел 2', decimal_num='1.2.3', astral_variant=self.variant)


class TestAstralPartForm(AstralPartTestBase):
    def test_form_valid(self):
        form = AstralPartForm(data={
            'name': 'Узел OK',
            'decimal_num': '9.9.9',
            'astral_variant': self.variant.id,
            'description': 'Тест',
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_decimal_num(self):
        form = AstralPartForm(data={
            'name': 'Узел BAD',
            'astral_variant': self.variant.id,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('decimal_num', form.errors)


class TestAstralPartViews(AstralPartTestBase):
    def test_create_view_requires_admin(self):
        url = reverse('main:astral_part_create')
        # Гость -> редирект на логин
        resp_guest = self.client.get(url)
        self.assertEqual(resp_guest.status_code, 302)
        # Пользователь без прав -> редирект (user_passes_test)
        self.client.login(username='user', password='pass')
        resp_user = self.client.get(url)
        self.assertEqual(resp_user.status_code, 302)

    def test_create_view_post_creates_part(self):
        self.client.login(username='admin', password='pass')
        url = reverse('main:astral_part_create')
        resp = self.client.post(url, data={
            'name': 'Созданный узел',
            'decimal_num': '2.3.4',
            'astral_variant': self.variant.id,
            'description': 'desc',
        })
        # после успешного создания — редирект на detail
        self.assertEqual(resp.status_code, 302)
        part = AstralPart.objects.get(decimal_num='2.3.4')
        self.assertEqual(part.name, 'Созданный узел')

    def test_edit_view_updates_part(self):
        self.client.login(username='admin', password='pass')
        part = AstralPart.objects.create(name='Old', decimal_num='7.7.7', astral_variant=self.variant)
        url = reverse('main:astral_part_edit', kwargs={'part_id': part.id})
        resp = self.client.post(url, data={
            'name': 'New',
            'decimal_num': '7.7.7',
            'astral_variant': self.variant.id,
            'description': '',
        })
        self.assertEqual(resp.status_code, 302)
        part.refresh_from_db()
        self.assertEqual(part.name, 'New')

    def test_list_view_search_by_decimal_num(self):
        self.client.login(username='admin', password='pass')
        AstralPart.objects.create(name='AAA', decimal_num='1.1.1', astral_variant=self.variant)
        AstralPart.objects.create(name='BBB', decimal_num='2.2.2', astral_variant=self.variant)
        url = reverse('main:astral_parts_list') + '?search=2.2.2'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Проверим, что второй есть в контексте
        parts = resp.context['parts']
        self.assertEqual(parts.count(), 1)
        self.assertEqual(parts.first().decimal_num, '2.2.2')

    def test_list_view_filter_by_variant(self):
        self.client.login(username='admin', password='pass')
        a1 = AstralPart.objects.create(name='A1', decimal_num='3.3.3', astral_variant=self.variant)
        a2 = AstralPart.objects.create(name='A2', decimal_num='4.4.4', astral_variant=self.variant2)
        url = reverse('main:astral_parts_list') + f'?variant={self.variant2.id}'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        parts = resp.context['parts']
        self.assertEqual(parts.count(), 1)
        self.assertEqual(parts.first().id, a2.id)
