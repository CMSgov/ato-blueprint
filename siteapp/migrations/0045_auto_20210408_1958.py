# Generated by Django 3.1.7 on 2021-04-08 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('siteapp', '0044_auto_20210314_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='version',
            field=models.CharField(blank=True, default='1.0', help_text="Project's version identifier", max_length=32, null=True),
        ),
    ]
