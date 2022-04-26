from pprint import pprint

from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from access_management.permission_constants import (
    PROJECT_ADMIN_GROUP,
    edit_project_permission,
    manage_project_users_permission,
    view_project_permission,
)
from access_management.utils import generate_groups_and_permission
from controls.models import Element
from controls.oscal import CatalogData
from siteapp.models import User


# TODO "PackageRename" rename class to Project
# once the old Project class in /siteapp/models has been removed
class Package(models.Model):
    title = models.CharField(
        max_length=100, help_text="Name of the project", unique=False
    )
    acronym = models.CharField(
        max_length=20, help_text="Acronym for the name of the project", unique=False
    )
    catalog = models.ForeignKey(
        CatalogData,
        related_name="used_by_projects",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Catalog of controls that the project uses",
    )
    components = models.ManyToManyField(
        Element,
        limit_choices_to={"element_type": "system_element"},
        related_name="used_by_projects",
        default=None,
        blank=True,
        help_text="Components that exist in the project",
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        default=None,
        related_name="projects_created",
        help_text="User id of the project creator",
    )
    IMPACT_LEVEL_CHOICES = [
        ("low", "Low"),
        ("moderate", "Moderate"),
        ("high", "High"),
        ("unknown", "Don't Know"),
    ]
    impact_level = models.CharField(
        choices=IMPACT_LEVEL_CHOICES,
        max_length=20,
        default=None,
        null=True,
        help_text="FISMA impact level of the project",
    )
    LOCATION_CHOICES = [
        ("cms_aws", "CMS AWS Commercial East-West"),
        ("govcloud", "CMS AWS GovCloud"),
        ("azure", "Microsoft Azure"),
        ("other", "Other"),
    ]
    location = models.CharField(
        choices=LOCATION_CHOICES,
        max_length=100,
        default=None,
        null=True,
        help_text="Where the project is located",
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True, null=True)

    class Meta:
        permissions = [
            manage_project_users_permission,
            edit_project_permission,
            view_project_permission,
        ]

    def __str__(self):
        return "%s id=%d" % (self.title, self.id)

    def get_absolute_url(self):
        return f"/packages/{self.id}"


@receiver(post_save, sender=Package)
def create_groups_for_project(sender, instance, **kwargs):
    print("*----- create_groups_for_project function -----*")
    pprint("---sender")
    pprint(sender)
    pprint("---instance")
    pprint(instance)
    pprint("---kwargs")
    pprint(kwargs)

    # only want to do this when a project is created
    if kwargs["created"]:
        try:
            # Create groups for project with associated permissions
            generate_groups_and_permission(
                instance._meta.model_name, str(instance.id), instance
            )

            # add the creator user to the project admin group by default
            project_admin_group = Group.objects.get(
                name=str(instance.id) + PROJECT_ADMIN_GROUP
            )
            pprint("---project_admin_group")
            pprint(project_admin_group)
            instance.creator.groups.add(project_admin_group)
            pprint("---1 user has manage permission?")
            pprint(instance.creator.has_perm(manage_project_users_permission, instance))
            pprint("---2 user has edit permission?")
            pprint(instance.creator.has_perm(edit_project_permission, instance))
            pprint("---3 user has view permission?")
            pprint(instance.creator.has_perm(view_project_permission, instance))

        except Exception as e:
            raise e
    else:
        print("Object not created yet.")
