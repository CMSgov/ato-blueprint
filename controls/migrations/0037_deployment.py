# Generated by Django 3.0.11 on 2021-01-14 09:42

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0036_historicalstatement'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the deployment', max_length=250, unique=True)),
                ('description', models.CharField(help_text='Brief description of the deployment', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, help_text='A UUID (a unique identifier) for the deployment.')),
                ('system', models.ForeignKey(blank=True, help_text='The system associated with the deployment.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deployments', to='controls.System')),
            ],
        ),
    ]
