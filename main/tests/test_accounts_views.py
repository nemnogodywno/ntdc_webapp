from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class TestAccountsViews(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='u', password='p', first_name='Иван')

    def test_login_get(self):
        resp = self.client.get(reverse('accounts:login'))
        self.assertEqual(resp.status_code, 200)

    def test_login_post_success(self):
        resp = self.client.post(reverse('accounts:login'), data={'username': 'u', 'password': 'p'})
        self.assertEqual(resp.status_code, 302)

    def test_logout(self):
        self.client.login(username='u', password='p')
        resp = self.client.get(reverse('accounts:logout'))
        self.assertEqual(resp.status_code, 302)
