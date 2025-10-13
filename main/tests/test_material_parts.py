from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.models import (
    AstralType, AstralVariant, AstralPart, AstralRevision,
    AstralManufacturer, AstralYear, MaterialPart
)


class TestMaterialParts(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
        self.user = User.objects.create_user(username='user', password='pass')
        self.type = AstralType.objects.create(name='Тип', code='T')
        self.variant = AstralVariant.objects.create(name='Вариант', code='V', astral_type=self.type)
        self.year2023 = AstralYear.objects.create(astral_variant=self.variant, year=2023)
        self.year2024 = AstralYear.objects.create(astral_variant=self.variant, year=2024)
        self.manuA = AstralManufacturer.objects.create(name='Завод A', code='A')
        self.manuB = AstralManufacturer.objects.create(name='Завод B', code='B')
        self.part = AstralPart.objects.create(name='Узел', decimal_num='1.2.3', astral_variant=self.variant)
        self.rev = AstralRevision.objects.create(name='Rev')
        self.rev.astral_parts.add(self.part)
        # Материальные узлы
        self.mp1 = MaterialPart.objects.create(
            serial='SNA', astral_revision=self.rev,
            astral_manufacturer=self.manuA, astral_year=self.year2023
        )
        self.mp2 = MaterialPart.objects.create(
            serial='SNB', astral_revision=self.rev,
            astral_manufacturer=self.manuB, astral_year=self.year2024
        )

    def test_list_requires_login(self):
        url = reverse('main:material_parts_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_list_filters(self):
        self.client.login(username='admin', password='pass')
        url = reverse('main:material_parts_list') + f'?manufacturer={self.manuA.id}&year={self.year2023.year}'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        parts = resp.context['parts']
        self.assertEqual(parts.count(), 1)
        self.assertEqual(parts.first().serial, 'SNA')

    def test_detail_ok(self):
        self.client.login(username='admin', password='pass')
        url = reverse('main:material_part_detail', kwargs={'part_id': self.mp1.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'SNA')

    def test_create_requires_admin(self):
        url = reverse('main:material_part_create')
        # guest
        self.assertEqual(self.client.get(url).status_code, 302)
        # user
        self.client.login(username='user', password='pass')
        self.assertEqual(self.client.get(url).status_code, 302)
        # admin create
        self.client.login(username='admin', password='pass')
        resp = self.client.post(url, data={
            'serial': 'SNC',
            'astral_revision': self.rev.id,
            'astral_year': self.year2024.id,
            'astral_manufacturer': self.manuA.id,
            'parent': ''
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(MaterialPart.objects.filter(serial='SNC').exists())

    def test_edit_updates(self):
        self.client.login(username='admin', password='pass')
        url = reverse('main:material_part_edit', kwargs={'part_id': self.mp1.id})
        resp = self.client.post(url, data={
            'serial': 'SNA-NEW',
            'astral_revision': self.rev.id,
            'astral_year': self.year2023.id,
            'astral_manufacturer': self.manuA.id,
            'parent': ''
        })
        self.assertEqual(resp.status_code, 302)
        self.mp1.refresh_from_db()
        self.assertEqual(self.mp1.serial, 'SNA-NEW')

    def test_delete_removes(self):
        self.client.login(username='admin', password='pass')
        url = reverse('main:material_part_delete', kwargs={'part_id': self.mp2.id})
        # confirm via POST
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(MaterialPart.objects.filter(id=self.mp2.id).exists())

