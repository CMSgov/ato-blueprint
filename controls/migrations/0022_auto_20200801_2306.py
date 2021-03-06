# Generated by Django 3.0.7 on 2020-08-01 23:06

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0021_statement_pid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="statement",
            name="pid",
            field=models.CharField(
                blank=True,
                help_text="Statement part identifier such as 'h' or 'h.1' or other part key",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="statement",
            name="sid",
            field=models.CharField(
                blank=True,
                help_text="Statement identifier such as OSCAL formatted Control ID",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="statement",
            name="sid_class",
            field=models.CharField(
                blank=True,
                help_text="Statement identifier 'class' such as 'NIST_SP-800-53_rev4' or other OSCAL catalog name Control ID ",
                max_length=200,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="Poam",
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
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="A UUID (a unique identifier) for this POAM.",
                    ),
                ),
                (
                    "statement",
                    models.ForeignKey(
                        help_text="The Poam details for this statement. Statement must be type POAM",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="poam",
                        to="controls.Statement",
                    ),
                ),
            ],
        ),
    ]
