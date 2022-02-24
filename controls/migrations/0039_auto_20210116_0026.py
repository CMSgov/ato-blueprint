# Generated by Django 3.0.11 on 2021-01-16 00:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0038_auto_20210114_1125"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deployment",
            name="system",
            field=models.ForeignKey(
                blank=True,
                help_text="The system associated with the deployment",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="deployments",
                to="controls.System",
            ),
        ),
    ]
