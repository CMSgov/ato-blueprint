# Generated by Django 2.2.12 on 2020-04-27 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0011_auto_20200425_0249"),
    ]

    operations = [
        migrations.AlterField(
            model_name="element",
            name="name",
            field=models.CharField(
                help_text="Common name or acronym of the element",
                max_length=250,
                unique=True,
            ),
        ),
    ]
