# Generated by Django 2.2.12 on 2020-04-17 16:15

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0003_auto_20200417_1418"),
    ]

    operations = [
        migrations.RenameField(
            model_name="commoncontrol",
            old_name="legacy_imp_stm",
            new_name="legacy_imp_smt",
        ),
        migrations.AlterField(
            model_name="commoncontrol",
            name="common_control_provider",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="controls.CommonControlProvider",
            ),
            preserve_default=False,
        ),
    ]
