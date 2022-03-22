from django.test import TestCase

from project.models import Package
from siteapp.models import User


class PackageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create()

        Package.objects.create(
            title="Pretty Ordinary Project",
            acronym="POP",
            impact_level="unknown",
            location="other",
            creator=User.objects.get(id=1),
        )

    # Tests for field labels
    def test_title_label(self):
        project = Package.objects.get(id=1)
        field_label = project._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "title")

    def test_acronym_label(self):
        project = Package.objects.get(id=1)
        field_label = project._meta.get_field("acronym").verbose_name
        self.assertEqual(field_label, "acronym")

    def test_impact_level_label(self):
        project = Package.objects.get(id=1)
        field_label = project._meta.get_field("impact_level").verbose_name
        self.assertEqual(field_label, "impact level")

    def test_location_label(self):
        project = Package.objects.get(id=1)
        field_label = project._meta.get_field("location").verbose_name
        self.assertEqual(field_label, "location")

    def test_creator_label(self):
        project = Package.objects.get(id=1)
        field_label = project._meta.get_field("creator_id").verbose_name
        self.assertEqual(field_label, "creator")

    def test_catalog_label(self):
        project = Package.objects.get(id=1)
        field_label = project._meta.get_field("catalog_id").verbose_name
        self.assertEqual(field_label, "catalog")

    def test_components_label(self):
        project = Package.objects.get(id=1)
        field_label = project._meta.get_field("components").verbose_name
        self.assertEqual(field_label, "components")

    def test_created_label(self):
        project = Package.objects.get(id=1)
        field_label = project._meta.get_field("created").verbose_name
        self.assertEqual(field_label, "created")

    def test_updated_label(self):
        project = Package.objects.get(id=1)
        field_label = project._meta.get_field("updated").verbose_name
        self.assertEqual(field_label, "updated")

    # Tests for max length
    def test_title_max_length(self):
        project = Package.objects.get(id=1)
        max_length = project._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)

    def test_acronym_max_length(self):
        project = Package.objects.get(id=1)
        max_length = project._meta.get_field("acronym").max_length
        self.assertEqual(max_length, 20)

    def test_impact_level_max_length(self):
        project = Package.objects.get(id=1)
        max_length = project._meta.get_field("impact_level").max_length
        self.assertEqual(max_length, 20)

    def test_location_max_length(self):
        project = Package.objects.get(id=1)
        max_length = project._meta.get_field("location").max_length
        self.assertEqual(max_length, 100)

    # Tests for model functions
    def test_object_str_returns_project_title_and_id(self):
        project = Package.objects.get(id=1)
        expected_object_name = f"{project.title} id={project.id}"

        self.assertEqual(str(project), expected_object_name)

    def test_get_absolute_url(self):
        test_id = 1
        expected_url = f"/packages/{test_id}"

        project = Package.objects.get(id=test_id)
        self.assertEqual(project.get_absolute_url(), expected_url)
