# Generated by Django 3.0.7 on 2021-01-05 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0034_auto_20201224_1551"),
    ]

    operations = [
        migrations.AddField(
            model_name="importrecord",
            name="name",
            field=models.CharField(
                blank=True,
                help_text="File name of the import",
                max_length=100,
                null=True,
            ),
        ),
    ]
