# Generated by Django 3.0.11 on 2021-01-14 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('siteapp', '0037_organizationalsetting'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='version',
            field=models.CharField(blank=True, help_text="Project's version identifier", max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='version_comment',
            field=models.TextField(blank=True, help_text="Project's version comment", null=True),
        ),
    ]
