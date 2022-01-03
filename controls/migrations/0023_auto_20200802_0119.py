# Generated by Django 3.0.7 on 2020-08-02 01:19

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0022_auto_20200801_2306'),
    ]

    def create_uuids(apps, schema_editor):
        Element = apps.get_model('controls', 'Element')
        for obj in Element.objects.all():
            obj.uuid = uuid.uuid4()
            obj.save()
        Statement = apps.get_model('controls', 'Statement')
        for obj in Statement.objects.all():
            obj.uuid = uuid.uuid4()
            obj.save()

    operations = [
        migrations.RemoveField(model_name='poam', name='uuid'),
        migrations.AddField(
            model_name='element',
            name='uuid',
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=True,
                help_text='A UUID (a unique identifier) for this Element.',
            ),
        ),
        migrations.AddField(
            model_name='statement',
            name='uuid',
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=True,
                help_text='A UUID (a unique identifier) for this Statement.',
            ),
        ),
        migrations.RunPython(create_uuids, migrations.RunPython.noop),
    ]
