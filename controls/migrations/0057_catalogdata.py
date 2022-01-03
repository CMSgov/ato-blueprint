# Generated by Django 3.2.4 on 2021-08-05 02:12

import django.db.models.manager
import jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0056_element_oscal_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catalog_key', models.CharField(help_text='Unique key for catalog', max_length=100, unique=True)),
                ('catalog_json', jsonfield.fields.JSONField(blank=True, help_text='JSON object representing the OSCAL-formatted control catalog.', null=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'prefetch_manager',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('prefetch_manager', django.db.models.manager.Manager()),
            ],
        ),
    ]
