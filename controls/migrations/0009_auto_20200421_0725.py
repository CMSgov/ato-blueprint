# Generated by Django 2.2.12 on 2020-04-21 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0008_auto_20200421_0134"),
    ]

    operations = [
        migrations.AddField(
            model_name="elementcontrol",
            name="oscal_catalog_key",
            field=models.CharField(
                blank=True,
                help_text="Catalog key from which catalog file can be derived (e.g., 'NIST_SP-800-53_rev4')",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="elementcontrol",
            unique_together={("element", "oscal_ctl_id", "oscal_catalog_key")},
        ),
        migrations.RemoveField(
            model_name="elementcontrol",
            name="oscal_catalog_id",
        ),
    ]
