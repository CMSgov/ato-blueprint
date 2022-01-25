import os

import requests
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.crypto import get_random_string
from selenium.common.exceptions import NoSuchElementException

from discussion.validators import VALID_EXTS, validate_file_extension
from guidedmodules.management.commands.load_modules import Command as load_modules
from guidedmodules.models import AppSource
from siteapp.models import User, Organization, Portfolio
from siteapp.tests import SeleniumTest, var_sleep
from siteapp.tests import wait_for_sleep_after

FIXTURE_DIR = "fixtures"
TEST_FILENAME = "test"
TEST_FILENAME_UPPER = "testupper"
TEST_SPECIAL_FILENAME = "test,.png"

class DiscussionTests(SeleniumTest):

    def setUp(self):
        super().setUp()
        # Load modules from the fixtures directory so that we have the required
        # modules as well as a test project.

        try:
            AppSource.objects.all().delete()
        except Exception as ex:
            print(f"Exception: {ex}")
            print(f"App Sources:{AppSource.objects.all()}")
        AppSource.objects.get_or_create(
              # this one exists on first db load because it's created by
              # migrations, but because the testing framework seems to
              # get rid of it after the first test in this class
            slug="system",
            is_system_source=True,
            defaults={
                "spec": { # required system projects
                    "type": "local",
                    "path": "fixtures/modules/system",
                }
            }
        )
        load_modules().handle() # load system modules

        AppSource.objects.create(
            slug="project",
            spec={
                "type": "local",
                "path": "fixtures/modules/other",
            }
        )\
        	.add_app_to_catalog("simple_project")

        # Create a default user that is a member of the organization.

        self.user_pw = get_random_string(4)
        self.user = User.objects.create(username="me")
        self.user.set_password(self.user_pw)
        # Grant user permission to view appsource
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        self.user.save()
        # Grant user permission to view appsource
        self.user.user_permissions.add(Permission.objects.get(codename='view_appsource'))

        # Create the Organization.

        _org = Organization.create(name="Our Organization", slug="testorg",
            admin_user=self.user)

        # Create a Portfolio and Grant Access
        portfolio = Portfolio.objects.create(title=self.user.username)
        portfolio.assign_owner_permissions(self.user)

    def test_validate_file_extension(self):
        # Load test file paths
        random_ext = ".random"

        for ext, _content_type in VALID_EXTS.items():
            print("Testing file type {}".format(ext))
            test_file_name = "".join([TEST_FILENAME, ext])
            test_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                FIXTURE_DIR,
                test_file_name
            )
            test_file_contents = b''

            # Read in test file
            with open(test_path, "rb") as test_file:
                test_file_contents = test_file.read()

            # Test valid file extension, content type
            file_model = SimpleUploadedFile(
                            test_file_name,
                            test_file_contents
                        )
            is_valid = validate_file_extension(file_model)

            #self.assertIsNone(is_valid)

            # Test valid file extension, unsupported type
            file_model = SimpleUploadedFile(
                            test_file_name,
                            b'\x7f\x45\x4c\x46\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        )
            is_valid = validate_file_extension(file_model)
            self.assertIsNotNone(is_valid)

            # Test invalid file extension, but valid content type
            file_model = SimpleUploadedFile(
                            "".join([test_file_name, random_ext]),
                            test_file_contents
                        )
            is_valid = validate_file_extension(file_model)
            self.assertIsNotNone(is_valid)

            # Test file extension not in defined valid extensions
            file_model = SimpleUploadedFile(
                            test_file_name,
                            test_file_contents
                        )
            _file, file_ext = os.path.splitext(test_file_name)
            content_types = VALID_EXTS[file_ext] # Save original content type
            VALID_EXTS[file_ext] = [] # Mock out list of valid content types
            is_valid = validate_file_extension(file_model)
            self.assertIsNotNone(is_valid)

            # Restore list of valid content types
            VALID_EXTS[file_ext] = content_types

        # Test uppercase extension
        for ext, _content_type in {".jpeg": ("image/jpeg",),}.items():
            print("Testing file type {}".format(ext))
            test_file_name = "".join([TEST_FILENAME_UPPER, ext.upper()])
            test_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                FIXTURE_DIR,
                test_file_name
            )
            test_file_contents = b''

            # Read in test file
            with open(test_path, "rb") as test_file:
                test_file_contents = test_file.read()
            # Test valid file extension, content type
            file_model = SimpleUploadedFile(
                            test_file_name,
                            test_file_contents
                        )
            is_valid = validate_file_extension(file_model)
            self.assertIsNone(is_valid)
