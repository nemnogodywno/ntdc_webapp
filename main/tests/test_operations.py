from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from main.models import (
    AstralType, AstralVariant, AstralPart, AstralRevision,
    AstralManufacturer, AstralYear, MaterialPart,
    MaterialGroup, MaterialOperationType, MaterialUser,
    MaterialStatus, MaterialWarehouse, MaterialOperations
)


class TestOperations(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
        self.user = User.objects.create_user(username='user', password='pass')
        # Базовые сущности для material_part
        self.type = AstralType.objects.create(name='Тип', code='T')
        self.variant = AstralVariant.objects.create(name='Вариант', code='V', astral_type=self.type)
        self.year = AstralYear.objects.create(astral_variant=self.variant, year=2024)
        self.manu = AstralManufacturer.objects.create(name='Завод', code='M')
        self.part = AstralPart.objects.create(name='Узел', decimal_num='1.2.3', astral_variant=self.variant)
        self.rev = AstralRevision.objects.create(name='Rev')
        self.rev.astral_parts.add(self.part)
        self.mpart = MaterialPart.objects.create(
            serial='SNO', astral_revision=self.rev,
            astral_manufacturer=self.manu, astral_year=self.year
        )
        # Справочники операций
        self.group = MaterialGroup.objects.create(name='Гр', description='')
        self.op_type = MaterialOperationType.objects.create(name='Операция', description='', material_group=self.group)
        self.mstatus = MaterialStatus.objects.create(name='Статус', description='')
        self.wh = MaterialWarehouse.objects.create(name='Склад', description='')
        self.muser = MaterialUser.objects.create(first_name='Иван', second_name='Иванов', patronymic='', material_group=self.group)

    def _mk_operation(self):
        return MaterialOperations.objects.create(
            material_operation_type=self.op_type,
            material_user=self.muser,
            datetime=timezone.now(),
            description='desc',
            material_status=self.mstatus,
            material_warehouse=self.wh,
            material_part=self.mpart,
        )

    def test_list_requires_login(self):
        url = reverse('main:operations_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_list_filters(self):
        self.client.login(username='admin', password='pass')
        op1 = self._mk_operation()
        url = reverse('main:operations_list') + f'?status={self.mstatus.id}&operation_type={self.op_type.id}'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Операция')

    def test_detail_requires_login(self):
        op = self._mk_operation()
        url = reverse('main:operation_detail', kwargs={'operation_id': op.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_create_requires_login_allows_user(self):
        url = reverse('main:operation_create')
        # guest redirect
        self.assertEqual(self.client.get(url).status_code, 302)
        # regular user can create (view protected only by login)
        self.client.login(username='user', password='pass')
        resp = self.client.post(url, data={
            'material_operation_type': self.op_type.id,
            'material_user': self.muser.id,
            'datetime': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'description': 'x',
            'material_status': self.mstatus.id,
            'material_warehouse': self.wh.id,
            'material_part': self.mpart.id,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(MaterialOperations.objects.count(), 1)

    def test_edit_requires_admin(self):
        op = self._mk_operation()
        url = reverse('main:operation_edit', kwargs={'operation_id': op.id})
        # regular user
        self.client.login(username='user', password='pass')
        self.assertEqual(self.client.get(url).status_code, 302)
        # admin can edit
        self.client.login(username='admin', password='pass')
        resp = self.client.post(url, data={
            'material_operation_type': self.op_type.id,
            'material_user': self.muser.id,
            'datetime': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'description': 'new',
            'material_status': self.mstatus.id,
            'material_warehouse': self.wh.id,
            'material_part': self.mpart.id,
        })
        self.assertEqual(resp.status_code, 302)
        op.refresh_from_db()
        self.assertEqual(op.description, 'new')

    def test_delete_requires_admin(self):
        op = self._mk_operation()
        url = reverse('main:operation_delete', kwargs={'operation_id': op.id})
        # user
        self.client.login(username='user', password='pass')
        self.assertEqual(self.client.get(url).status_code, 302)
        # admin
        self.client.login(username='admin', password='pass')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(MaterialOperations.objects.filter(id=op.id).exists())

