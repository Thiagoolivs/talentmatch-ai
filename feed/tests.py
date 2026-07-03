from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import CompanyProfile, Notification

from .models import Post, PostComment, PostLike

User = get_user_model()


@override_settings(SECURE_SSL_REDIRECT=False)
class FeedTests(TestCase):
    def setUp(self):
        self.company = User.objects.create_user(
            username='empresa', email='empresa@example.com', password='x',
            user_type='company', email_verified=True,
        )
        CompanyProfile.objects.create(
            user=self.company, company_name='TechCorp', verification_status='approved',
        )
        self.candidate = User.objects.create_user(
            username='candidato', email='cand@example.com', password='x',
            user_type='candidate', email_verified=True,
        )

    def test_feed_requires_login(self):
        response = self.client.get(reverse('feed:index'))
        self.assertEqual(response.status_code, 302)

    def test_feed_renders(self):
        self.client.force_login(self.candidate)
        response = self.client.get(reverse('feed:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comunidade')

    def test_approved_company_can_post(self):
        self.client.force_login(self.company)
        response = self.client.post(reverse('feed:create_post'), {'content': 'Estamos contratando!'})
        self.assertRedirects(response, reverse('feed:index'))
        self.assertEqual(Post.objects.count(), 1)

    def test_candidate_cannot_post(self):
        self.client.force_login(self.candidate)
        self.client.post(reverse('feed:create_post'), {'content': 'oi'})
        self.assertEqual(Post.objects.count(), 0)

    def test_unapproved_company_cannot_post(self):
        pending = User.objects.create_user(
            username='pendente', email='p@example.com', password='x',
            user_type='company', email_verified=True,
        )
        CompanyProfile.objects.create(user=pending, company_name='Pendente SA')
        self.client.force_login(pending)
        self.client.post(reverse('feed:create_post'), {'content': 'oi'})
        self.assertEqual(Post.objects.count(), 0)

    def test_like_toggle(self):
        post = Post.objects.create(author=self.company, content='post')
        self.client.force_login(self.candidate)
        url = reverse('feed:toggle_like', args=[post.id])

        response = self.client.post(url)
        self.assertEqual(response.json(), {'liked': True, 'count': 1})

        response = self.client.post(url)
        self.assertEqual(response.json(), {'liked': False, 'count': 0})

    def test_comment_notifies_author(self):
        post = Post.objects.create(author=self.company, content='post')
        self.client.force_login(self.candidate)
        self.client.post(reverse('feed:add_comment', args=[post.id]), {'content': 'Legal!'})
        self.assertEqual(PostComment.objects.count(), 1)
        self.assertTrue(Notification.objects.filter(user=self.company).exists())

    def test_only_author_or_staff_deletes_post(self):
        post = Post.objects.create(author=self.company, content='post')

        self.client.force_login(self.candidate)
        self.client.post(reverse('feed:delete_post', args=[post.id]))
        self.assertEqual(Post.objects.count(), 1)

        self.client.force_login(self.company)
        self.client.post(reverse('feed:delete_post', args=[post.id]))
        self.assertEqual(Post.objects.count(), 0)

    def test_comment_delete_permissions(self):
        post = Post.objects.create(author=self.company, content='post')
        comment = PostComment.objects.create(post=post, user=self.candidate, content='oi')

        other = User.objects.create_user(
            username='outro', email='o@example.com', password='x',
            user_type='candidate', email_verified=True,
        )
        self.client.force_login(other)
        self.client.post(reverse('feed:delete_comment', args=[comment.id]))
        self.assertEqual(PostComment.objects.count(), 1)

        # autor do post pode moderar comentários
        self.client.force_login(self.company)
        self.client.post(reverse('feed:delete_comment', args=[comment.id]))
        self.assertEqual(PostComment.objects.count(), 0)


@override_settings(SECURE_SSL_REDIRECT=False)
class CompanyPageTests(TestCase):
    def setUp(self):
        self.company = User.objects.create_user(
            username='empresa2', email='e2@example.com', password='x',
            user_type='company', email_verified=True,
        )
        CompanyProfile.objects.create(
            user=self.company, company_name='DataCorp', verification_status='approved',
        )

    def test_company_page_renders(self):
        response = self.client.get(reverse('core:company_detail', args=[self.company.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'DataCorp')

    def test_company_page_404_for_candidate(self):
        candidate = User.objects.create_user(
            username='cand2', email='c2@example.com', password='x',
            user_type='candidate', email_verified=True,
        )
        response = self.client.get(reverse('core:company_detail', args=[candidate.id]))
        self.assertEqual(response.status_code, 404)
