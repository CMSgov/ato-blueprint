# Generated by Django 3.0.7 on 2020-06-07 19:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0014_auto_20200504_0003"),
    ]

    operations = [
        migrations.CreateModel(
            name="ElementCommonControl",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "oscal_ctl_id",
                    models.CharField(
                        blank=True,
                        help_text="OSCAL formatted Control ID (e.g., au-2.3)",
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "oscal_catalog_key",
                    models.CharField(
                        blank=True,
                        help_text="Catalog key from which catalog file can be derived (e.g., 'NIST_SP-800-53_rev4')",
                        max_length=100,
                        null=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "common_control",
                    models.ForeignKey(
                        help_text="The Common Control for this association.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="element_common_control",
                        to="controls.CommonControl",
                    ),
                ),
                (
                    "element",
                    models.ForeignKey(
                        help_text="The Element (e.g., System, Component, Host) to which common controls are associated.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="common_controls",
                        to="controls.Element",
                    ),
                ),
            ],
            options={
                "unique_together": {
                    ("element", "common_control", "oscal_ctl_id", "oscal_catalog_key")
                },
            },
        ),
    ]
