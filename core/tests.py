from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()


@override_settings(SECURE_SSL_REDIRECT=False)
class SmokeTests(TestCase):
    """Verifica que as páginas principais renderizam sem erro."""

    def test_public_pages(self):
        for name in ['core:home', 'core:about', 'core:contact', 'accounts:login',
                     'accounts:register', 'jobs:list', 'courses:list']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_authenticated_pages(self):
        user = User.objects.create_user(
            username='smoke', email='smoke@example.com', password='x',
            user_type='candidate', email_verified=True,
        )
        self.client.force_login(user)
        for name in ['dashboard:index', 'accounts:profile', 'chatbot:chat',
                     'chatbot:history', 'messaging:list', 'feed:index',
                     'jobs:my_applications', 'courses:my_courses']:
            response = self.client.get(reverse(name), follow=True)
            self.assertEqual(response.status_code, 200, name)

    def test_job_list_pagination_preserves_filters(self):
        response = self.client.get(reverse('jobs:list'), {'job_type': 'full_time'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['query_string'], 'job_type=full_time')
