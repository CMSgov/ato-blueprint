# Generated by Django 3.2.5 on 2022-02-09 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0065_elementcontrol_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementcontrol',
            name='status',
            field=models.IntegerField(choices=[(2, 'Pending'), (3, 'Implemented'), (4, 'Assessed'), (5, 'Changes requested')], default=2),
        ),
    ]
