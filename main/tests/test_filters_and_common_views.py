from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.templatetags.b64filters import b64encode


class TestTemplateFilters(TestCase):
    def test_b64encode_bytes(self):
        out = b64encode(b'abc')
        self.assertEqual(out, 'YWJj')

    def test_b64encode_empty(self):
        self.assertEqual(b64encode(None), '')
        self.assertEqual(b64encode(b''), '')


class TestCommonViews(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', is_staff=True)
        self.user = User.objects.create_user(username='user', password='pass')

    def test_home_view(self):
        resp = self.client.get(reverse('main:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('total_parts', resp.context)
        self.assertIn('total_operations', resp.context)
        self.assertIn('total_revisions', resp.context)

    def test_dashboard_requires_login(self):
        url = reverse('main:dashboard')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.login(username='user', password='pass')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('recent_operations', resp.context)

    def test_admin_panel_access(self):
        url = reverse('main:admin_panel')
        # guest
        self.assertEqual(self.client.get(url).status_code, 302)
        # non-admin
        self.client.login(username='user', password='pass')
        self.assertEqual(self.client.get(url).status_code, 302)
        # admin
        self.client.login(username='admin', password='pass')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('astral_types', resp.context)
        self.assertIn('material_groups', resp.context)

