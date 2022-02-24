# Generated by Django 2.2.12 on 2020-04-20 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0006_statement_elements"),
    ]

    operations = [
        migrations.AlterField(
            model_name="statement",
            name="elements",
            field=models.ManyToManyField(
                blank=True, null=True, related_name="statements", to="controls.Element"
            ),
        ),
    ]
