# Generated by Django 3.2.4 on 2021-08-05 15:19

import jsonfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0057_catalogdata"),
    ]

    operations = [
        migrations.AddField(
            model_name="catalogdata",
            name="baselines_json",
            field=jsonfield.fields.JSONField(
                blank=True,
                help_text="JSON object representing the baselines for the catalog.",
                null=True,
            ),
        ),
    ]
