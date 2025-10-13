from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.models import AstralType, AstralVariant, AstralPart, AstralRevision
from main.forms import AstralRevisionForm


class TestAstralRevision(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
        self.user = User.objects.create_user(username='user', password='pass')
        self.type = AstralType.objects.create(name='Тип X', code='TX')
        self.variant = AstralVariant.objects.create(name='Вариант X', code='VX', astral_type=self.type)
        self.part1 = AstralPart.objects.create(name='Узел A', decimal_num='10.20', astral_variant=self.variant)
        self.part2 = AstralPart.objects.create(name='Узел B', decimal_num='10.30', astral_variant=self.variant)

    def test_form_valid_with_parts(self):
        form = AstralRevisionForm(data={
            'name': 'Rev 1',
            'description': 'desc',
            'astral_parts': [self.part1.id, self.part2.id],
            'parent': '',
            'release_date': '',
        })
        self.assertTrue(form.is_valid())

    def test_list_search_by_part_name(self):
        rev = AstralRevision.objects.create(name='R1')
        rev.astral_parts.add(self.part1)
        self.client.login(username='admin', password='pass')
        url = reverse('main:astral_revisions_list') + '?search=Узел A'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'R1')

    def test_create_view_admin_only(self):
        url = reverse('main:astral_revision_create')
        # guest
        self.assertEqual(self.client.get(url).status_code, 302)
        # regular user
        self.client.login(username='user', password='pass')
        self.assertEqual(self.client.get(url).status_code, 302)
        # admin create
        self.client.login(username='admin', password='pass')
        resp = self.client.post(url, data={
            'name': 'R2',
            'astral_parts': [self.part1.id],
            'description': ''
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(AstralRevision.objects.filter(name='R2').exists())

    def test_edit_view(self):
        self.client.login(username='admin', password='pass')
        rev = AstralRevision.objects.create(name='Old')
        rev.astral_parts.add(self.part1)
        url = reverse('main:astral_revision_edit', kwargs={'revision_id': rev.id})
        resp = self.client.post(url, data={
            'name': 'New',
            'astral_parts': [self.part1.id, self.part2.id],
            'description': 'updated'
        })
        self.assertEqual(resp.status_code, 302)
        rev.refresh_from_db()
        self.assertEqual(rev.name, 'New')
        self.assertEqual(rev.astral_parts.count(), 2)

    def test_delete_view_admin_only_and_deletes(self):
        rev = AstralRevision.objects.create(name='ToDelete')
        rev.astral_parts.add(self.part1)
        url = reverse('main:astral_revision_delete', kwargs={'revision_id': rev.id})
        # guest
        self.assertEqual(self.client.get(url).status_code, 302)
        # user
        self.client.login(username='user', password='pass')
        self.assertEqual(self.client.get(url).status_code, 302)
        # admin POST delete
        self.client.login(username='admin', password='pass')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(AstralRevision.objects.filter(id=rev.id).exists())
