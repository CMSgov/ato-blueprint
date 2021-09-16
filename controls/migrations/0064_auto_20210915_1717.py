# Generated by Django 3.2.5 on 2021-09-15 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0063_inheritance'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalstatement',
            name='inheritance',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='controls.inheritance'),
        ),
        migrations.AddField(
            model_name='statement',
            name='inheritance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statements', to='controls.inheritance'),
        ),
    ]
