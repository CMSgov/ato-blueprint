# Generated by Django 2.2.12 on 2020-04-17 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="commoncontrol",
            name="common_control_provider",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="controls.CommonControlProvider",
            ),
        ),
    ]
