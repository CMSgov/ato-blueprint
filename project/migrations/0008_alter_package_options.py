# Generated by Django 3.2.5 on 2022-02-14 17:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_auto_20220214_1741'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='package',
            options={'permissions': [('can_add_members', 'Can add members')]},
        ),
    ]
