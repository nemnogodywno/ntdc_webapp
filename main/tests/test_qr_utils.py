from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from main.models import (
    AstralType, AstralVariant, AstralPart, AstralRevision,
    AstralManufacturer, AstralYear, MaterialPart
)
from main.qr_utils import (
    get_astral_revision_url_qr, get_astral_revision_info_qr,
    get_material_part_url_qr, get_material_part_info_qr
)


class TestQRUtils(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='u', password='p')
        self.type = AstralType.objects.create(name='Тип', code='T')
        self.variant = AstralVariant.objects.create(name='Вариант', code='V', astral_type=self.type)
        self.part = AstralPart.objects.create(name='Узел', decimal_num='1.2.3', astral_variant=self.variant)
        self.rev = AstralRevision.objects.create(name='Rev')
        self.rev.astral_parts.add(self.part)
        self.manu = AstralManufacturer.objects.create(name='Завод', code='M1')
        self.year = AstralYear.objects.create(astral_variant=self.variant, year=2024)
        self.mpart = MaterialPart.objects.create(
            serial='SN123',
            astral_revision=self.rev,
            astral_manufacturer=self.manu,
            astral_year=self.year,
            parent=None,
        )

    def _req(self, path='/'):
        req = self.rf.get(path, HTTP_HOST='testserver')
        return req

    def test_astral_revision_url_qr(self):
        data_url = get_astral_revision_url_qr(self.rev, self._req())
        self.assertIsInstance(data_url, str)
        self.assertTrue(data_url.startswith('data:image/png;base64,'))

    def test_astral_revision_info_qr(self):
        data_url = get_astral_revision_info_qr(self.rev)
        self.assertIsInstance(data_url, str)
        self.assertTrue(data_url.startswith('data:image/png;base64,'))

    def test_material_part_url_qr(self):
        data_url = get_material_part_url_qr(self.mpart, self._req())
        self.assertIsInstance(data_url, str)
        self.assertTrue(data_url.startswith('data:image/png;base64,'))

    def test_material_part_info_qr(self):
        data_url = get_material_part_info_qr(self.mpart)
        self.assertIsInstance(data_url, str)
        self.assertTrue(data_url.startswith('data:image/png;base64,'))

