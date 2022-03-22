from django.test import TestCase
from django.urls import reverse

from project.models import Package
from siteapp.models import User


class ProjectViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user = User.objects.create_user(
            username="testuser",
            password="password",
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )

        # Create a project
        Package.objects.create(
            title="Rapid Rabbit",
            acronym="RR",
            location="other",
            impact_level="low",
            creator=test_user,
        )

    def test_redirect_if_not_logged_in(self):
        projects = Package.objects.all()
        test_project_id = projects[0].id
        test_project_url = f"/packages/{test_project_id}/"

        response = self.client.get(test_project_url)
        self.assertRedirects(response, f"/accounts/login/?next={test_project_url}")

    def test_view_url_exists_at_desired_location(self):
        projects = Package.objects.all()
        test_project_id = projects[0].id
        test_project_url = f"/packages/{test_project_id}/"

        logged_in = self.client.login(username="testuser", password="password")
        self.assertTrue(logged_in)

        response = self.client.get(test_project_url)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        projects = Package.objects.all()
        test_project_id = projects[0].id

        self.client.login(username="testuser", password="password")

        response = self.client.get(
            reverse("project_homepage", kwargs={"project_id": test_project_id})
        )
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        projects = Package.objects.all()
        test_project_id = projects[0].id

        self.client.login(username="testuser", password="password")

        response = self.client.get(
            reverse("project_homepage", kwargs={"project_id": test_project_id})
        )
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, "project/project-home.html")


class CreateProjectViewTest(TestCase):
    def setUp(self):
        # Create a user
        User.objects.create_user(
            username="testuser",
            password="password",
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )

    def test_redirect_if_not_logged_in(self):
        attempted_url = "/packages/create"
        response = self.client.get(attempted_url)
        self.assertRedirects(response, f"/accounts/login/?next={attempted_url}")

    def test_view_url_exists_at_desired_location(self):
        logged_in = self.client.login(username="testuser", password="password")
        self.assertTrue(logged_in)

        response = self.client.get("/packages/create")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("create_project"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("create_project"))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, "project/project-create.html")

    def test_can_submit_with_baseline_required_data_fields(self):
        required_data = {
            "title": "Rapid Rabbit",
            "acronym": "RR",
            "location": "other",
            "impact_level": "low",
        }
        expected_count_of_projects_in_database = 1

        self.client.login(username="testuser", password="password")
        self.client.post("/packages/create", required_data)
        self.assertEqual(
            Package.objects.count(), expected_count_of_projects_in_database
        )

    def test_CANNOT_submit_with_missing_title_field(self):
        data_without_title = {
            "acronym": "RR",
            "location": "other",
            "impact_level": "low",
        }
        expected_count_of_projects_in_database = 0

        self.client.login(username="testuser", password="password")
        self.client.post("/packages/create", data_without_title)
        self.assertEqual(
            Package.objects.count(), expected_count_of_projects_in_database
        )

    def test_CANNOT_submit_with_missing_acronym_field(self):
        data_without_acronym = {
            "title": "Rapid Rabbit",
            "location": "other",
            "impact_level": "low",
        }
        expected_count_of_projects_in_database = 0

        self.client.login(username="testuser", password="password")
        self.client.post("/packages/create", data_without_acronym)
        self.assertEqual(
            Package.objects.count(), expected_count_of_projects_in_database
        )

    def test_CANNOT_submit_with_missing_location_field(self):
        data_without_location = {
            "title": "Rapid Rabbit",
            "acronym": "RR",
            "impact_level": "low",
        }
        expected_count_of_projects_in_database = 0

        self.client.login(username="testuser", password="password")
        self.client.post("/packages/create", data_without_location)
        self.assertEqual(
            Package.objects.count(), expected_count_of_projects_in_database
        )

    def test_CANNOT_submit_with_missing_impact_level_field(self):
        data_without_impact_level = {
            "title": "Rapid Rabbit",
            "acronym": "RR",
            "location": "other",
        }
        expected_count_of_projects_in_database = 0

        self.client.login(username="testuser", password="password")
        self.client.post("/packages/create", data_without_impact_level)
        self.assertEqual(
            Package.objects.count(), expected_count_of_projects_in_database
        )

    def test_redirects_to_projects_page_on_success(self):
        required_data = {
            "title": "Rapid Rabbit",
            "acronym": "RR",
            "location": "other",
            "impact_level": "low",
        }

        self.client.login(username="testuser", password="password")
        response = self.client.post("/packages/create", required_data)
        self.assertRedirects(response, reverse("projects"))
