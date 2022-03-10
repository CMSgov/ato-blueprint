from django.test import TestCase
from django.urls import reverse

from siteapp.models import User

# from django.contrib.auth.models import Permission

class CreateProjectViewTest(TestCase):
    def setUp(self):
        # Create a user
        User.objects.create_user(username='testuser', password='password', is_superuser=True, is_staff=True, is_active=True)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get('/project/create')
        self.assertRedirects(response, '/accounts/login/?next=/project/create')

    def test_view_url_exists_at_desired_location(self):
        logged_in = self.client.login(username='testuser', password='password')
        self.assertTrue(logged_in)

        response = self.client.get('/project/create')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        logged_in = self.client.login(username='testuser', password='password')
        self.assertTrue(logged_in)

        response = self.client.get(reverse('create_project'))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'project/project-create.html')
