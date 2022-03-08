# from asyncio.windows_events import NULL

from cgi import test

from django.test import Client, TestCase

# import uuid
from django.urls import reverse

# from project.models import Package
from siteapp.models import User

# from django.contrib.auth.models import Permission

class CreateProjectViewTest(TestCase):
    # def setUp(cls):
    #     # Create a user
    #     cls.test_user = User.objects.create()
    #     test_user1 = User.objects.create_user(username='testuser', password='password', is_superuser=True, is_staff=True, is_active=True)
    #     test_user1.save()

    #     users = User.objects.all()
    #     print("Total users actually in the database=" + str(users.count()))
    #     for  user in users:
    #         print('Actually-inserted user: ' + str(user))

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser', password='password', is_superuser=True, is_staff=True, is_active=True)
        test_user1.save()

        u = User(username="username")
        u.set_password("password")
        u.save()

        users = User.objects.all()
        print("Total users actually in the database=" + str(users.count()))
        for  user in users:
            print('Actually-inserted user: ' + str(user.password))

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        logged_in = self.client.login(username='testuser', password='password')

        self.assertTrue(logged_in)
        # c = Client()
        # response = c.get('/projects')
        # response = self.client.get(reverse('create_project'))
        # self.assertEqual(response.status_code, 200)
        # response = c.get('/projects')
        # print("----------------")
        # print(response['location'])
        # print("----------------")
        # self.assertEqual(response.status_code, 200)

    # def test_redirect_if_not_logged_in(self):
    #     self.client.login(username='testuser1', password='password')
    #     response = self.client.get(reverse('projects'))
    #     self.assertRedirects(response, '/login')

    # def test_uses_correct_template(self):
    #     login = self.client.login(username='testuser1', password='password')
    #     print("----------------")
    #     print(reverse('create_project'))
    #     print("----------------")
    #     testResponse = self.client.get('/')
    #     print(testResponse)
    #     testResponse2 = self.client.get('/project/create')
    #     print(testResponse2)

    #     response = self.client.get(reverse('create_project'))
    #     self.assertEqual(response.status_code, 200)

    #     # Check we used correct template
    #     self.assertTemplateUsed(response, 'project/project-create.html')
